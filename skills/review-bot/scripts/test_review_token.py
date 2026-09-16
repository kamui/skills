#!/usr/bin/env python3
"""Exercise review_token.py through its command-line interface against a fake forge.

Usage: python3 scripts/test_review_token.py [-v]
Inputs: a throwaway RSA key from `openssl genrsa` and an http.server fake forge
reached through --api and REVIEW_BOT_CACHE_DIR; nothing outside the temp dir.
Exit 0: checks pass; 1: assertion failure; 2: openssl or a subprocess cannot run.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SCRIPT = SCRIPTS / "review_token.py"
CLIENT_ID = "Iv1.testclientid"
INSTALLED = "acme/widgets"
UNAUTHORIZED = "acme/locked"


def expires_in(seconds: int) -> str:
    when = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=seconds)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


class Forge(ThreadingHTTPServer):
    """A fake forge that records every request and the tokens it minted."""

    def __init__(self):
        super().__init__(("127.0.0.1", 0), Handler)
        self.requests: list[tuple[str, str, str]] = []
        self.jwts: list[str] = []
        self.tokens: list[str] = []
        self.refuse_probe = False
        self.lock = threading.Lock()

    @property
    def url(self) -> str:
        return "http://127.0.0.1:%d" % self.server_address[1]


class Handler(BaseHTTPRequestHandler):
    server: Forge

    def log_message(self, *args):
        pass

    def bearer(self) -> str:
        header = self.headers.get("Authorization", "")
        return header[len("Bearer "):] if header.startswith("Bearer ") else ""

    def reply(self, status: int, document: dict) -> None:
        body = json.dumps(document).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def route(self, method: str) -> None:
        path = self.path
        if path.startswith("/api/v3/"):
            path = path[len("/api/v3"):]
        elif path == "/api/graphql":
            path = "/graphql"
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8") if length else ""
        with self.server.lock:
            self.server.requests.append((method, self.path, body))
            if method == "GET" and path == "/app":
                self.server.jwts.append(self.bearer())
                return self.reply(200, {"name": "Reviewer App", "slug": "reviewer"})
            if method == "GET" and path.startswith("/repos/") and path.endswith("/installation"):
                self.server.jwts.append(self.bearer())
                repo = path[len("/repos/"):-len("/installation")]
                if repo in (INSTALLED, UNAUTHORIZED):
                    return self.reply(200, {"id": 42, "permissions": {"pull_requests": "write", "issues": "write"}})
                return self.reply(404, {"message": "Not Found"})
            if method == "POST" and path == "/app/installations/42/access_tokens":
                self.server.jwts.append(self.bearer())
                if json.loads(body)["repositories"] == [UNAUTHORIZED.split("/")[1]]:
                    return self.reply(401, {"message": "Bad credentials"})
                token = "ghs_test%d" % (len(self.server.tokens) + 1)
                self.server.tokens.append(token)
                return self.reply(201, {"token": token, "expires_at": expires_in(3600), "permissions": {"pull_requests": "write"}})
            if method == "POST" and path == "/graphql":
                if self.bearer() in self.server.tokens and not self.server.refuse_probe:
                    return self.reply(200, {"data": {"viewer": {"login": "reviewer"}}})
                return self.reply(401, {"message": "Bad credentials"})
            return self.reply(404, {"message": "no route for %s %s" % (method, self.path)})

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")


class ReviewToken(unittest.TestCase):
    forge: Forge

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.key = cls.root / "app.pem"
        cls.public = cls.root / "app.pub"
        cls.other_key = cls.root / "other.pem"
        try:
            subprocess.run(["openssl", "genrsa", "-out", str(cls.key), "2048"], check=True, capture_output=True)
            subprocess.run(["openssl", "genrsa", "-out", str(cls.other_key), "2048"], check=True, capture_output=True)
            subprocess.run(["openssl", "rsa", "-in", str(cls.key), "-pubout", "-out", str(cls.public)], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError) as error:
            print("openssl genrsa could not run: %s" % error, file=sys.stderr)
            sys.exit(2)
        cls.key.chmod(0o600)
        cls.other_key.chmod(0o600)
        cls.forge = Forge()
        cls.thread = threading.Thread(target=cls.forge.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.forge.shutdown()
        cls.forge.server_close()
        cls.temp.cleanup()

    def setUp(self):
        self.case = Path(tempfile.mkdtemp(dir=self.root))
        self.cache = self.case / "cache"
        with self.forge.lock:
            self.forge.requests.clear()
            self.forge.jwts.clear()
            self.forge.tokens.clear()
            self.forge.refuse_probe = False

    def run_script(self, *args: str, env: dict | None = None, api: str | None = None, key: bool = True):
        environment = {
            "PATH": os.environ["PATH"],
            "HOME": str(self.case / "home"),
            "REVIEW_BOT_CACHE_DIR": str(self.cache),
        }
        environment.update(env or {})
        command = [sys.executable, str(SCRIPT), args[0], "--client-id", CLIENT_ID, "--api", api or self.forge.url]
        if key:
            command += ["--key", str(self.key)]
        command += list(args[1:])
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=environment)

    def mints(self) -> int:
        with self.forge.lock:
            return sum(1 for method, path, _ in self.forge.requests if method == "POST" and path.endswith("/access_tokens"))

    def cache_file(self) -> Path:
        owner, name = INSTALLED.split("/")
        return self.cache / CLIENT_ID / owner / (name + ".json")

    def test_token_mints_prints_only_the_token_and_signs_a_valid_jwt(self):
        result = self.run_script("token", INSTALLED)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "ghs_test1\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.mints(), 1)
        self.assertEqual(json.loads(self.cache_file().read_text(encoding="utf-8"))["token"], "ghs_test1")
        with self.forge.lock:
            jwt = self.forge.jwts[0]
        header, claims, signature = jwt.split(".")

        def decode(part: str) -> bytes:
            return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))

        self.assertEqual(json.loads(decode(header)), {"alg": "RS256", "typ": "JWT"})
        body = json.loads(decode(claims))
        now = int(dt.datetime.now(dt.timezone.utc).timestamp())
        self.assertEqual(body["iss"], CLIENT_ID)
        self.assertLessEqual(body["iat"], now)
        self.assertGreater(body["exp"], now)
        self.assertLessEqual(body["exp"] - body["iat"], 600)
        signature_file = self.case / "sig.bin"
        signature_file.write_bytes(decode(signature))
        verify = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", str(self.public), "-signature", str(signature_file)],
            input=("%s.%s" % (header, claims)).encode("ascii"),
            capture_output=True,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)

    def test_fresh_cache_is_reused_and_stale_or_disabled_cache_re_mints(self):
        first = self.run_script("token", INSTALLED)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_script("token", INSTALLED)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, first.stdout)
        self.assertEqual(self.mints(), 1)
        with self.forge.lock:
            self.assertEqual(len(self.forge.requests), 2, "the cached token reached the forge for nothing")

        record = json.loads(self.cache_file().read_text(encoding="utf-8"))
        record["expires_at"] = expires_in(120)
        self.cache_file().write_text(json.dumps(record), encoding="utf-8")
        stale = self.run_script("token", INSTALLED)
        self.assertEqual(stale.returncode, 0, stale.stderr)
        self.assertEqual(stale.stdout, "ghs_test2\n")
        self.assertEqual(self.mints(), 2)

        disabled = self.run_script("token", INSTALLED, env={"REVIEW_BOT_NO_CACHE": "1"})
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertEqual(disabled.stdout, "ghs_test3\n")
        self.assertEqual(self.mints(), 3)

    def test_cache_directories_are_700_and_files_600(self):
        result = self.run_script("token", INSTALLED)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.cache_file()
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        for directory in (path.parent, path.parent.parent, self.cache):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700, directory)
        self.assertFalse(path.with_name(path.name + ".part").exists())

    def test_unwritable_cache_still_prints_the_token(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root ignores directory modes")
        self.cache.mkdir()
        self.cache.chmod(0o500)
        try:
            result = self.run_script("token", INSTALLED)
        finally:
            self.cache.chmod(0o700)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "ghs_test1\n")
        self.assertIn("cannot write the token cache", result.stderr)
        self.assertFalse(self.cache_file().exists())

    def test_key_resolution_order(self):
        home = self.case / "home"
        config = home / ".config" / "review-bot"
        config.mkdir(parents=True)
        not_a_key = self.case / "not-a-key.pem"
        not_a_key.write_text("not a key\n", encoding="utf-8")

        (config / "key.pem").write_bytes(self.key.read_bytes())
        (config / "key.pem").chmod(0o600)
        result = self.run_script("token", INSTALLED, key=False)
        self.assertEqual(result.returncode, 0, "key.pem fallback: " + result.stderr)

        (config / "key.pem").write_bytes(not_a_key.read_bytes())
        result = self.run_script("token", INSTALLED, key=False, env={"REVIEW_BOT_NO_CACHE": "1"})
        self.assertEqual(result.returncode, 2, "key.pem is not a key: " + result.stderr)
        (config / (CLIENT_ID + ".pem")).write_bytes(self.key.read_bytes())
        (config / (CLIENT_ID + ".pem")).chmod(0o600)
        result = self.run_script("token", INSTALLED, key=False, env={"REVIEW_BOT_NO_CACHE": "1"})
        self.assertEqual(result.returncode, 0, "<client id>.pem beats key.pem: " + result.stderr)

        (config / (CLIENT_ID + ".pem")).write_bytes(not_a_key.read_bytes())
        result = self.run_script("token", INSTALLED, key=False, env={"REVIEW_BOT_NO_CACHE": "1"})
        self.assertEqual(result.returncode, 2, "<client id>.pem is not a key: " + result.stderr)
        result = self.run_script(
            "token", INSTALLED, key=False, env={"REVIEW_BOT_NO_CACHE": "1", "REVIEW_BOT_KEY": str(self.key)}
        )
        self.assertEqual(result.returncode, 0, "REVIEW_BOT_KEY beats the config dir: " + result.stderr)

        result = self.run_script(
            "token", INSTALLED, "--key", str(self.other_key), env={"REVIEW_BOT_NO_CACHE": "1", "REVIEW_BOT_KEY": str(not_a_key)},
            key=False,
        )
        self.assertEqual(result.returncode, 0, "--key beats REVIEW_BOT_KEY: " + result.stderr)

    def test_missing_key_exits_2_naming_the_path(self):
        result = self.run_script("token", INSTALLED, key=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        expected = self.case / "home" / ".config" / "review-bot" / (CLIENT_ID + ".pem")
        self.assertIn(str(expected), result.stderr)
        self.assertEqual(self.mints(), 0)

        explicit = self.case / "nowhere.pem"
        result = self.run_script("token", INSTALLED, "--key", str(explicit), key=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(explicit), result.stderr)

    def test_non_key_file_exits_2_naming_openssl(self):
        not_a_key = self.case / "not-a-key.pem"
        not_a_key.write_text("not a key\n", encoding="utf-8")
        not_a_key.chmod(0o600)
        result = self.run_script("token", INSTALLED, "--key", str(not_a_key), key=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("openssl", result.stderr)
        self.assertIn(str(not_a_key), result.stderr)
        self.assertEqual(self.mints(), 0)

    def test_shared_key_warns_on_stderr(self):
        shared = self.case / "shared.pem"
        shared.write_bytes(self.key.read_bytes())
        shared.chmod(0o644)
        result = self.run_script("token", INSTALLED, "--key", str(shared), key=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "ghs_test1\n")
        self.assertIn("readable by other users", result.stderr)

    def test_not_installed_exits_1_naming_the_repository(self):
        result = self.run_script("token", "acme/elsewhere")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("not installed on acme/elsewhere", result.stderr)

    def test_refused_token_exchange_exits_1_with_status_and_message(self):
        result = self.run_script("token", UNAUTHORIZED)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("HTTP 401", result.stderr)
        self.assertIn("Bad credentials", result.stderr)

    def test_unreachable_forge_exits_2(self):
        result = self.run_script("token", INSTALLED, api="http://127.0.0.1:9")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("network failure", result.stderr)

    def test_whoami_prints_both_logins_and_the_installation(self):
        shared = self.case / "shared.pem"
        shared.write_bytes(self.key.read_bytes())
        shared.chmod(0o644)
        result = self.run_script("whoami", INSTALLED, "--key", str(shared), key=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], "app: Reviewer App (reviewer)")
        self.assertEqual(lines[1], "rest login: reviewer[bot]")
        self.assertEqual(lines[2], "graphql login: reviewer")
        self.assertEqual(lines[3], "installation: 42 on acme/widgets")
        self.assertEqual(lines[4], "permissions: issues: write, pull_requests: write")
        self.assertEqual(
            lines[5],
            "review-token command: python3 %s token --client-id %s acme/widgets" % (shlex.quote(str(SCRIPT)), CLIENT_ID),
        )
        with self.forge.lock:
            paths = [path for _, path, _ in self.forge.requests]
        self.assertIn("/graphql", paths)
        self.assertNotIn("/api/graphql", paths)
        self.assertEqual(paths.count("/repos/acme/widgets/installation"), 1, paths)
        self.assertEqual(result.stderr.count("readable by other users"), 1, "whoami signed more than one JWT")

    def test_whoami_derives_the_enterprise_graphql_url(self):
        result = self.run_script("whoami", INSTALLED, api=self.forge.url + "/api/v3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("graphql login: reviewer\n", result.stdout)
        with self.forge.lock:
            paths = [path for _, path, _ in self.forge.requests]
        self.assertIn("/api/graphql", paths)
        self.assertIn("/api/v3/app", paths)
        self.assertNotIn("/graphql", paths)

    def test_whoami_with_a_refused_probe_exits_1(self):
        with self.forge.lock:
            self.forge.refuse_probe = True
        result = self.run_script("whoami", INSTALLED)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("the minted token failed the probe", result.stderr)
        self.assertEqual(self.mints(), 1)

    def test_whoami_replaces_a_cached_token_the_probe_refuses(self):
        first = self.run_script("token", INSTALLED)
        self.assertEqual(first.returncode, 0, first.stderr)
        with self.forge.lock:
            self.forge.tokens[0] = "revoked"
        result = self.run_script("whoami", INSTALLED)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("graphql login: reviewer\n", result.stdout)
        self.assertIn("the cached token failed the probe", result.stderr)
        self.assertIn(str(self.cache_file()), result.stderr)
        self.assertEqual(self.mints(), 2)
        self.assertEqual(json.loads(self.cache_file().read_text(encoding="utf-8"))["token"], "ghs_test2")

    def test_whoami_still_re_mints_when_the_cached_token_cannot_be_removed(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root ignores directory modes")
        first = self.run_script("token", INSTALLED)
        self.assertEqual(first.returncode, 0, first.stderr)
        with self.forge.lock:
            self.forge.tokens[0] = "revoked"
        self.cache_file().parent.chmod(0o500)
        try:
            result = self.run_script("whoami", INSTALLED)
        finally:
            self.cache_file().parent.chmod(0o700)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("graphql login: reviewer\n", result.stdout)
        self.assertIn("cannot remove the token cache", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.mints(), 2)

    def test_repository_must_be_owner_slash_repo(self):
        for bad in ("widgets", "acme/", "/widgets", "a/b/c", "../x"):
            result = self.run_script("token", bad)
            self.assertEqual(result.returncode, 2, bad)
            self.assertEqual(result.stdout, "", bad)


if __name__ == "__main__":
    unittest.main()
