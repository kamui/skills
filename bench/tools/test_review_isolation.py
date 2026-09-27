#!/usr/bin/env python3
"""Verify isolation boundaries through hooks and a local fake model API.

Usage: python3 bench/tools/test_review_isolation.py
       BENCH_ISOLATION_CLI=/path/to/claude python3 bench/tools/test_review_isolation.py

The optional integration checks execute the real CLI against localhost with a dummy
key. They contact no model provider. Put bwrap and socat on PATH first.
Exit codes: 0 tests pass; 1 failure. Integration tests skip without the explicit CLI.
"""

from __future__ import annotations

import http.server
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

import review_isolation


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="review-isolation-")
        self.root = Path(self.temp.name).resolve()
        self.attempt = self.root / "attempt"
        self.clone = self.attempt / "clone"
        self.work = self.attempt / "clone-work"
        for path in (self.clone, self.work, self.attempt / "tmp", self.attempt / "artifacts", self.attempt / "home"):
            path.mkdir(parents=True, exist_ok=True)
        self.outside = self.root / "outside"
        self.outside.write_text("PRIVATE_CANARY_DO_NOT_READ", encoding="utf-8")
        self.clone.joinpath("tracked").write_text("original", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def decision(self, tool, **inputs):
        event = {"tool_name": tool, "tool_input": inputs, "cwd": str(self.clone)}
        done = subprocess.run([sys.executable, str(Path(review_isolation.__file__)), "hook", "--attempt", str(self.attempt), "--clone", str(self.clone)],
                              input=json.dumps(event), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)["hookSpecificOutput"]["permissionDecision"] if done.stdout else None

    def test_file_access_and_clone_write_boundaries(self):
        self.assertIsNone(self.decision("Read", file_path="tracked"))
        self.assertIsNone(self.decision("Write", file_path=str(self.work / "new"), content="scratch"))
        self.assertEqual(self.decision("Read", file_path=str(self.outside)), "deny")
        self.assertEqual(self.decision("Write", file_path="tracked", content="changed"), "deny")
        self.assertEqual(self.decision("Edit", file_path=str(self.attempt / "isolation-settings.json")), "deny")
        self.assertEqual(self.decision("WebFetch", url="https://example.com"), "deny")

    def test_symlink_and_recursive_search_escapes(self):
        (self.work / "link").symlink_to(self.outside)
        for tool in ("Read", "Write", "Edit"):
            self.assertEqual(self.decision(tool, file_path=str(self.work / "link")), "deny")
        for tool in ("Grep", "Glob"):
            self.assertEqual(self.decision(tool, path=str(self.work), pattern="*"), "deny")
        self.assertEqual(self.decision("Glob", path=str(self.clone), pattern="../../*"), "deny")

    def test_malformed_hook_input_fails_closed(self):
        done = subprocess.run([sys.executable, str(Path(review_isolation.__file__)), "hook", "--attempt", str(self.attempt), "--clone", str(self.clone)],
                              input="not json", capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(done.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_runtime_caches_move_outside_the_clone(self):
        subprocess.run(["git", "init", "-q", str(self.clone)], check=True, capture_output=True)
        (self.clone / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        modules = self.clone / "packages/example/node_modules"
        modules.mkdir(parents=True)
        review_isolation.prepare_runtime_cache(self.clone)
        review_isolation.prepare_runtime_cache(self.clone)
        for name in (".vite-temp", ".vite"):
            self.assertTrue((modules / name).is_symlink())
            self.assertTrue(review_isolation.contained(modules / name, [self.work]))
        (self.clone / ".gitignore").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must be git-ignored"):
            review_isolation.prepare_runtime_cache(self.clone)

    def test_shell_allowance(self):
        self.assertEqual(self.decision("Bash", command="sleep 1000", timeout=1000000), "deny")
        self.assertEqual(self.decision("Bash", command="true", run_in_background=True), "deny")


class LocalModel(http.server.ThreadingHTTPServer):
    def __init__(self, responses):
        self.responses = iter(responses)
        self.results = {}
        super().__init__(("127.0.0.1", 0), ModelHandler)


class ModelHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if "messages" not in self.path:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")
            return
        for message in data.get("messages", []):
            blocks = message.get("content", [])
            for block in blocks if isinstance(blocks, list) else []:
                if block.get("type") == "tool_result":
                    self.server.results[block["tool_use_id"]] = block
        blocks = next(self.server.responses, [{"type": "text", "text": "Fixture complete."}])
        reason = "tool_use" if any(b["type"] == "tool_use" for b in blocks) else "end_turn"
        message = {"id": "msg_fixture", "type": "message", "role": "assistant", "model": "claude-sonnet-5",
                   "content": [], "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}}
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        self.event("message_start", {"message": message})
        for index, block in enumerate(blocks):
            if block["type"] == "tool_use":
                start = {**block, "input": {}}
                delta = {"type": "input_json_delta", "partial_json": json.dumps(block["input"])}
            else:
                start, delta = {"type": "text", "text": ""}, {"type": "text_delta", "text": block["text"]}
            self.event("content_block_start", {"index": index, "content_block": start})
            self.event("content_block_delta", {"index": index, "delta": delta})
            self.event("content_block_stop", {"index": index})
        self.event("message_delta", {"delta": {"stop_reason": reason, "stop_sequence": None}, "usage": {"output_tokens": 1}})
        self.event("message_stop", {})

    def event(self, kind, payload):
        self.wfile.write(("event: " + kind + "\ndata: " + json.dumps({"type": kind, **payload}) + "\n\n").encode())


def call(identifier, name, **inputs):
    return {"type": "tool_use", "id": identifier, "name": name, "input": inputs}


@unittest.skipUnless(os.environ.get("BENCH_ISOLATION_CLI"), "set BENCH_ISOLATION_CLI for the free real-CLI checks")
class NativeIsolation(Boundaries):
    def run_cli(self, responses):
        config = self.attempt / "isolation-settings.json"
        config.write_text(json.dumps(review_isolation.settings(self.attempt, self.clone)), encoding="utf-8")
        home = self.attempt / "home"
        (home / ".claude.json").write_text('{"hasCompletedOnboarding": true}', encoding="utf-8")
        server = LocalModel(responses)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        env = {k: os.environ[k] for k in ("PATH", "LD_LIBRARY_PATH", "LANG") if k in os.environ}
        env.update(HOME=str(home), ANTHROPIC_BASE_URL=f"http://127.0.0.1:{server.server_port}", ANTHROPIC_API_KEY="test-not-a-key",
                   DISABLE_AUTOUPDATER="1", CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1", CLAUDE_CODE_TMPDIR=str(self.attempt / "tmp"))
        try:
            done = subprocess.run([os.environ["BENCH_ISOLATION_CLI"], "-p", "Execute the fixture tools.", "--model", "claude-sonnet-5",
                                   "--effort", "high", "--settings", str(config), "--setting-sources", "user", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                                   "--tools", ",".join(review_isolation.TOOLS), "--allowedTools", ",".join(review_isolation.TOOLS),
                                   "--output-format", "stream-json", "--verbose"],
                                  cwd=self.work, env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(done.returncode, 0, done.stderr + done.stdout[-2000:])
            self.assertNotIn("PRIVATE_CANARY_DO_NOT_READ", done.stdout)
            return server.results
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_allowed_shell_and_file_tools(self):
        results = self.run_cli([[call("scratch", "Bash", command=f"printf scratch > {self.work}/allowed; cat {self.work}/allowed"),
                                 call("read", "Read", file_path=str(self.clone / "tracked")),
                                 call("write", "Write", file_path=str(self.work / "written"), content="scratch")]])
        self.assertFalse(results["scratch"].get("is_error"), results)
        self.assertFalse(results["read"].get("is_error"), results)
        self.assertFalse(results["write"].get("is_error"), results)
        self.assertEqual((self.work / "allowed").read_text(), "scratch")
        self.assertEqual((self.work / "written").read_text(), "scratch")

    def test_native_shell_filesystem_and_network_denials(self):
        script = "import pathlib,socket; "
        script += f"p=pathlib.Path(bytes({list(str(self.outside).encode())}).decode()); "
        script += "print(p.read_text())"
        results = self.run_cli([[call("outside", "Bash", command="python3 -c " + shlex.quote(script)),
                                 call("clone", "Bash", command="python3 -c " + shlex.quote(f"open({str(self.clone / 'tracked')!r},'w').write('changed')")),
                                 call("network", "Bash", command="python3 -c 'import socket; socket.create_connection((\"1.1.1.1\",80),timeout=1)'"),
                                 call("file", "Read", file_path=str(self.outside))]])
        for identifier in ("outside", "clone", "network", "file"):
            self.assertTrue(results[identifier].get("is_error"), results)
        self.assertRegex(results["outside"]["content"], "PermissionError|FileNotFoundError")
        self.assertEqual((self.clone / "tracked").read_text(), "original")

    def test_worker_inherits_file_hook(self):
        results = self.run_cli([[call("worker", "Agent", subagent_type="general-purpose", model="sonnet", description="Exercise inherited isolation",
                                      prompt="Execute the fixture tool.", run_in_background=False)],
                               [call("worker_read", "Read", file_path=str(self.outside)),
                                call("worker_shell", "Bash", command="python3 -c 'import socket; socket.create_connection((\"1.1.1.1\",80),timeout=1)'")]])
        self.assertIn("worker", results)
        self.assertTrue(results["worker_read"].get("is_error"), results)
        self.assertIn("Benchmark isolation", results["worker_read"]["content"])
        self.assertTrue(results["worker_shell"].get("is_error"), results)

    def test_frozen_skill_loads_from_fresh_home(self):
        skill = self.attempt / "home/.claude/skills/review-code"
        skill.mkdir(parents=True)
        archive = subprocess.run(["git", "-C", str(Path(__file__).resolve().parents[2]), "archive", "c3c53da5381dace16876b0f5b7abe4bccc6bc58b"],
                                 check=True, capture_output=True)
        subprocess.run(["tar", "-x", "-C", str(skill)], input=archive.stdout, check=True, capture_output=True)
        results = self.run_cli([[call("frozen_skill", "Skill", skill="review-code", args="mode one-shot; profile publishable; return_format artifacts")]])
        self.assertIn("frozen_skill", results)
        self.assertFalse(results["frozen_skill"].get("is_error"), results)

    @unittest.skipUnless(os.environ.get("BENCH_ISOLATION_TARGETS"), "set BENCH_ISOLATION_TARGETS for frozen-target smoke checks")
    def test_frozen_target_smokes(self):
        import provision
        for name in os.environ["BENCH_ISOLATION_TARGETS"].split(","):
            with self.subTest(target=name):
                probe = NativeIsolation("test_allowed_shell_and_file_tools")
                probe.setUp()
                try:
                    shutil.rmtree(probe.clone)
                    target = provision.load_target(str(Path(__file__).resolve().parents[1] / "targets" / name))
                    prepared = provision.prepare(target, provision.DEFAULT_CACHE_ROOT, str(probe.clone))
                    self.assertFalse(prepared["failures"], prepared)
                    review_isolation.prepare_runtime_cache(probe.clone)
                    config = provision.cache_config(target)
                    substitutions = provision.substitutions(str(probe.clone) + "-cache", provision.DEFAULT_CACHE_ROOT, str(probe.clone), str(probe.work))
                    env = {k: provision.render(v, substitutions) for k, v in config["env"].items()}
                    command = "cd " + shlex.quote(str(probe.clone)) + " && "
                    command += "".join(k + "=" + shlex.quote(v) + " " for k, v in env.items()) + config["smoke"][0]["command"]
                    base = probe.work / "base"
                    clone_command = shlex.join(["git", "clone", "--quiet", "--no-hardlinks", str(probe.clone), str(base)])
                    clone_command += " && " + shlex.join(["git", "-C", str(base), "checkout", "--quiet", "main"])
                    results = probe.run_cli([[call("smoke", "Bash", command=command, timeout=300000),
                                              call("local_base_clone", "Bash", command=clone_command, timeout=300000)]])
                    clean = not provision.git("-C", str(probe.clone), "status", "--porcelain").strip()
                    record = {"target": name, "source": "real CLI with local fake API; no model inference", "billed_usd": 0,
                              "prepared": prepared, "command": command, "results": results, "tree_clean_after": clean}
                    if os.environ.get("BENCH_ISOLATION_EVIDENCE"):
                        output = Path(os.environ["BENCH_ISOLATION_EVIDENCE"])
                        output.mkdir(parents=True, exist_ok=True)
                        (output / (name + ".json")).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                    for result in results.values():
                        self.assertFalse(result.get("is_error"), results)
                    self.assertEqual(set(results), {"smoke", "local_base_clone"})
                    self.assertTrue(clean)
                finally:
                    probe.tearDown()


if __name__ == "__main__":
    unittest.main()
