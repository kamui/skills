#!/usr/bin/env python3
"""Allow-list HTTP/CONNECT proxy that logs every egress attempt of one review cell.

A reviewer cell must run offline against everything except the model provider: the
target's own upstream repository holds the later fix, the forge holds the review
that followed the pinned cutoff, and either would contaminate the measurement. The
runtime's own controls do not provide that boundary — a cell configured like the
#137 runner reaches the public internet from its shell (probe 2b) — so the cell is
launched with ``HTTPS_PROXY``/``HTTP_PROXY``/``ALL_PROXY`` pointing at this proxy,
which forwards only to the allow-listed provider hosts and refuses everything else.

Every attempt, allowed or refused, is appended to the log as one JSON object with
its timestamp, client port, method, target host and port, and decision. The log is
the cell's egress evidence: a refused line is a recorded isolation event, and any
request that never appears in it while the transcript shows network use means the
cell escaped the proxy and its attempt is invalid.

This is a boundary for an honest worker plus an audit trail for a dishonest one:
a process that unsets the proxy variables or dials an IP address directly is not
stopped by it, which is why the frozen protocol also audits the transcript.

Usage::

    python3 scripts/egress_proxy.py --port 8118 --log egress.jsonl \\
        --allow .anthropic.com --allow statsig.com [--host 127.0.0.1]
    python3 scripts/egress_proxy.py --self-test

``--allow`` takes a host suffix (``.anthropic.com`` matches ``api.anthropic.com``)
or an exact host name. Ports are restricted to 443 unless ``--allow-port`` names
another. The proxy prints ``listening <host>:<port>`` on stdout once it is ready,
then serves until it is terminated.

Exit: 0 on a clean shutdown, 1 on a content violation (no allow-list, unusable
log path) with one line per violation on stdout, 2 when the socket cannot be
bound, naming the address on stderr.
"""
from __future__ import annotations

import argparse
import json
import select
import socket
import socketserver
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

BUFFER = 65536
LOG_LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


class Handler(socketserver.StreamRequestHandler):
    timeout = 120

    def log(self, record):
        record["observed_at"] = now()
        record["client_port"] = self.client_address[1]
        line = json.dumps(record, sort_keys=True) + "\n"
        with LOG_LOCK:
            with open(self.server.log_path, "a", encoding="utf-8") as stream:
                stream.write(line)
                stream.flush()

    def allowed(self, host, port):
        if port not in self.server.ports:
            return False
        host = host.lower().rstrip(".")
        for pattern in self.server.allow:
            if pattern.startswith(".") and (host.endswith(pattern) or host == pattern[1:]):
                return True
            if host == pattern:
                return True
        return False

    def refuse(self, method, host, port, reason):
        self.log({"method": method, "host": host, "port": port, "decision": "refused", "reason": reason})
        body = ("egress to %s:%s is not on this cell's allow list" % (host, port)).encode("utf-8")
        self.wfile.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: " +
                         str(len(body)).encode("ascii") + b"\r\nConnection: close\r\n\r\n" + body)

    def handle(self):
        try:
            request = self.rfile.readline(BUFFER).decode("latin-1").strip()
        except OSError:
            return
        parts = request.split()
        if len(parts) < 2:
            return
        method, target = parts[0], parts[1]
        if method.upper() != "CONNECT":
            # Absolute-form plain HTTP: never forwarded, always logged and refused.
            host = target.split("//", 1)[-1].split("/", 1)[0]
            name, _, port = host.partition(":")
            self.refuse(method.upper(), name, int(port) if port.isdigit() else 80, "plaintext http is not forwarded")
            return
        name, _, port = target.partition(":")
        port = int(port) if port.isdigit() else 443
        if not self.allowed(name, port):
            self.refuse("CONNECT", name, port, "host or port not on the allow list")
            return
        try:
            upstream = socket.create_connection((name, port), timeout=30)
        except OSError as exc:
            self.log({"method": "CONNECT", "host": name, "port": port,
                      "decision": "allowed", "reason": "upstream connect failed: %s" % exc})
            self.wfile.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n")
            return
        self.log({"method": "CONNECT", "host": name, "port": port, "decision": "allowed", "reason": ""})
        # Drain the rest of the request headers before tunnelling.
        while True:
            line = self.rfile.readline(BUFFER)
            if line in (b"\r\n", b"\n", b""):
                break
        self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        self.wfile.flush()
        self.tunnel(self.connection, upstream)

    @staticmethod
    def tunnel(client, upstream):
        sockets = [client, upstream]
        try:
            while True:
                readable, _, broken = select.select(sockets, [], sockets, 60)
                if broken or not readable:
                    break
                for source in readable:
                    data = source.recv(BUFFER)
                    if not data:
                        return
                    (upstream if source is client else client).sendall(data)
        except OSError:
            return
        finally:
            for stream in sockets:
                try:
                    stream.close()
                except OSError:
                    pass


class Proxy(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(host, port, allow, ports, log_path):
    server = Proxy((host, port), Handler)
    server.allow, server.ports, server.log_path = allow, ports, log_path
    print("listening %s:%d" % server.server_address[:2], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def self_test():
    """Start the proxy on an ephemeral port and check both decisions."""
    import http.client
    import tempfile

    log = Path(tempfile.mkdtemp()) / "egress.jsonl"
    server = Proxy(("127.0.0.1", 0), Handler)
    server.allow, server.ports, server.log_path = [".example.com"], {443}, str(log)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    checks = []
    for target, expected in (("api.github.com:443", 403), ("evil.example.com:80", 403)):
        connection = http.client.HTTPConnection(host, port, timeout=10)
        connection.request("CONNECT", target)
        checks.append(("refuses " + target, connection.getresponse().status == expected))
        connection.close()
    connection = http.client.HTTPConnection(host, port, timeout=10)
    connection.request("GET", "http://api.github.com/rate_limit")
    checks.append(("refuses plaintext http", connection.getresponse().status == 403))
    connection.close()
    server.shutdown()
    server.server_close()
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    checks.append(("logs every attempt", len(records) == 3 and
                   all(record["decision"] == "refused" for record in records)))
    checks.append(("log carries host and reason", records[0]["host"] == "api.github.com" and
                   bool(records[0]["reason"])))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8118)
    parser.add_argument("--allow", action="append", default=[],
                        help="allowed host name, or host suffix beginning with a dot")
    parser.add_argument("--allow-port", action="append", type=int, default=[])
    parser.add_argument("--log", help="JSONL egress log for this cell")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    violations = []
    if not args.allow:
        violations.append("--allow is required: an empty allow list refuses the provider too")
    if not args.log:
        violations.append("--log is required: the egress log is the cell's isolation evidence")
    if violations:
        print("\n".join(violations))
        return 1
    try:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        Path(args.log).touch()
    except OSError as exc:
        print(exc)
        return 1
    try:
        return serve(args.host, args.port, [a.lower() for a in args.allow],
                     set(args.allow_port or [443]), args.log)
    except OSError as exc:
        print("%s:%d" % (args.host, args.port), file=sys.stderr)
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
