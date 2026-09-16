#!/usr/bin/env python3
"""Exercise the fenced-shell-block launcher through its command-line interface.

Usage: python3 scripts/test_run_block.py [-v]
Inputs: temporary Markdown references and the installed addressing protocol.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import re


SCRIPTS = Path(__file__).resolve().parent
LAUNCHER = SCRIPTS / "run_block.py"
ADDRESSING = SCRIPTS.parent / "references" / "addressing-protocol.md"
FENCE = re.compile(r"```sh\n(.*?)```", re.DOTALL)
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=([^\s]+)")


class RunBlock(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def reference(self, body: str) -> Path:
        path = self.root / "reference.md"
        path.write_text("# Fixture\n\n```sh\n%s\n```\n" % body, encoding="utf-8")
        return path

    def launch(self, reference: Path, marker: str, *bindings: str):
        return subprocess.run(
            [sys.executable, str(LAUNCHER), str(reference), "--marker", marker, "--", *bindings],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_value_with_shell_metacharacters_arrives_intact(self):
        value = "a space ' quote `tick` $(touch pwned) $HOME"
        reference = self.reference(
            "value=<input> literal=kept\n"
            "# <name> <kind> outside the assignment line is not a placeholder\n"
            "printf '%s\\n' \"$value\" \"$literal\" '<name> <kind>'"
        )
        result = self.launch(reference, "printf", "input=" + value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, value + "\nkept\n<name> <kind>\n")
        self.assertFalse((self.root / "pwned").exists())

    def test_marker_must_select_exactly_one_fence(self):
        reference = self.root / "selection.md"
        reference.write_text(
            "```sh\nvalue=<input>\necho first marker\n```\n\n"
            "```sh\nvalue=<input>\necho second marker\n```\n",
            encoding="utf-8",
        )
        for marker, count in (("absent", 0), ("marker", 2)):
            with self.subTest(count=count):
                result = self.launch(reference, marker, "input=x")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("run_block:", result.stderr)
                self.assertIn(str(reference), result.stderr)
                self.assertIn(repr(marker), result.stderr)
                self.assertIn(f"matched {count} sh fences", result.stderr)

    def test_binding_names_must_match_before_execution(self):
        reference = self.reference("first=<one> second=<two>\ntouch ran")
        for bindings, message in ((["one=1"], "missing two"),
                                  (["one=1", "two=2", "three=3"], "extra three")):
            with self.subTest(bindings=bindings):
                result = self.launch(reference, "touch ran", *bindings)
                self.assertEqual(result.returncode, 2)
                self.assertIn("run_block:", result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse((self.root / "ran").exists())

    def test_block_status_is_passed_through(self):
        reference = self.reference("status=<code>\nexit \"$status\"")
        for status in (0, 1, 2, 3):
            with self.subTest(status=status):
                result = self.launch(reference, "exit", f"code={status}")
                self.assertEqual(result.returncode, status)
                self.assertNotIn("run_block:", result.stderr)

    def test_launcher_status_two_has_its_prefix(self):
        reference = self.reference("value=<input>\nprintf '%s\\n' \"$value\"")
        result = self.launch(reference, "printf")
        self.assertEqual(result.returncode, 2)
        self.assertIn("run_block:", result.stderr)
        self.assertIn("missing input", result.stderr)

    def test_placeholder_line_must_be_unique(self):
        cases = {
            "none": "echo marker",
            "two": "first=<one>\nsecond=<two>\necho marker",
        }
        for name, body in cases.items():
            with self.subTest(case=name):
                reference = self.reference(body)
                result = self.launch(reference, "marker", "one=1", "two=2")
                self.assertEqual(result.returncode, 2)
                self.assertIn("run_block:", result.stderr)

    def test_real_blocks_have_one_sound_placeholder_line(self):
        text = ADDRESSING.read_text(encoding="utf-8")
        expected = {
            "flatten.py": {"owner", "repo", "n"},
            "check-runs": {"private-dir", "sha"},
            "write-loop.sh": {"private-dir", "pr"},
        }
        for marker, names in expected.items():
            with self.subTest(marker=marker):
                blocks = [body for body in FENCE.findall(text) if marker in body]
                self.assertEqual(len(blocks), 1)
                block = blocks[0]
                placeholder_lines = []
                for line in block.splitlines():
                    tokens = line.split()
                    matches = [ASSIGNMENT.fullmatch(token) for token in tokens]
                    if tokens and all(matches) and any(re.fullmatch(r"<[^<>]+>", match.group(1))
                                                       for match in matches if match):
                        placeholder_lines.append(matches)
                self.assertEqual(len(placeholder_lines), 1)
                actual = {match.group(1)[1:-1] for match in placeholder_lines[0]
                          if match and re.fullmatch(r"<[^<>]+>", match.group(1))}
                self.assertEqual(actual, names)
                self.assertFalse(self.top_level_positional_uses(block))

    @staticmethod
    def top_level_positional_uses(block: str) -> list[str]:
        kept, heredoc, in_function = [], None, False
        for line in block.splitlines():
            if heredoc is not None:
                if line == heredoc:
                    heredoc = None
                continue
            match = re.search(r"<<'([^']+)'", line)
            if match:
                kept.append(line[:match.start()])
                heredoc = match.group(1)
                continue
            if in_function:
                if line == "}":
                    in_function = False
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\(\) \{", line):
                in_function = True
                continue
            kept.append(line)
        program = "\n".join(kept)
        uses = re.findall(r"\$(?:[1-9][0-9]*|@)", program)
        uses += re.findall(r"(?:^|[;&|]\s*)(shift|set\s+--)(?:\s|$)", program, re.MULTILINE)
        return uses


if __name__ == "__main__":
    try:
        unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[sys.argv[0]])
    except OSError as error:
        print(f"test_run_block: cannot run a subprocess: {error}", file=sys.stderr)
        raise SystemExit(2)
