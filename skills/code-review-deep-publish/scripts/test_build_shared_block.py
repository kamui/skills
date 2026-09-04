#!/usr/bin/env python3
"""CLI regression tests for build_shared_block.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "build_shared_block.py"


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def invoke_argv(repo: Path, base_sha: str, head_sha: str, *extra: str) -> list[str]:
    return [
        sys.executable,
        str(SCRIPT),
        "--repo",
        str(repo),
        "--base-ref",
        "main",
        "--base-sha",
        base_sha,
        "--head-sha",
        head_sha,
        "--merge-base",
        base_sha,
        "--finding-format",
        "/tmp/finding-format.md",
        *extra,
    ]


def invoke(
    repo: Path,
    base_sha: str,
    head_sha: str,
    *extra: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        invoke_argv(repo, base_sha, head_sha, *extra),
        capture_output=True,
        check=False,
        text=True,
    )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory) / "repo"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.name", "Shared Block Test")
        git(repo, "config", "user.email", "shared-block@example.test")

        (repo / "src/pkg").mkdir(parents=True)
        (repo / "other").mkdir()
        (repo / "CONTRIBUTING.md").write_text("root guidance\n", encoding="utf-8")
        (repo / "src/AGENTS.md").write_text("scoped guidance\n", encoding="utf-8")
        (repo / "other/AGENTS.md").write_text("irrelevant guidance\n", encoding="utf-8")
        (repo / "src/pkg/app.py").write_text("print('old')\n", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "Seed fixture")
        base_sha = git(repo, "rev-parse", "HEAD")
        root_blob = git(repo, "rev-parse", f"{base_sha}:CONTRIBUTING.md")
        scoped_blob = git(repo, "rev-parse", f"{base_sha}:src/AGENTS.md")

        (repo / "src/pkg/app.py").write_text("print('new')\n", encoding="utf-8")
        git(repo, "add", "src/pkg/app.py")
        git(repo, "commit", "-q", "-m", "Change app")
        head_sha = git(repo, "rev-parse", "HEAD")

        result = invoke(repo, base_sha, head_sha)
        if result.returncode != 0:
            failures.append(f"normal invocation exited {result.returncode}: {result.stderr.strip()}")
        else:
            expected = (
                "## Pinned run identity",
                "## Changed-file manifest",
                "## Commit list",
                "## Full diff",
                "## Applicable base-branch guidance",
                "## Finding format",
            )
            positions = [result.stdout.find(heading) for heading in expected]
            if any(position < 0 for position in positions) or positions != sorted(positions):
                failures.append(f"sections are missing or out of order: {positions}")
            for fragment in (
                f"- base SHA: `{base_sha}`",
                f"- head SHA: `{head_sha}`",
                "M\tsrc/pkg/app.py",
                f"{head_sha} Change app",
                "+print('new')",
                f"### `CONTRIBUTING.md` (base blob `{root_blob}`)",
                f"### `src/AGENTS.md` (base blob `{scoped_blob}`)",
                "root guidance",
                "scoped guidance",
                "/tmp/finding-format.md",
            ):
                if fragment not in result.stdout:
                    failures.append(f"normal output is missing {fragment!r}")
            if "irrelevant guidance" in result.stdout:
                failures.append("guidance outside changed-path ancestors was included")

        (repo / "src/pkg/latin1.c").write_bytes(b"/* caf\xe9 */\nint x;\n")
        git(repo, "add", "src/pkg/latin1.c")
        git(repo, "commit", "-q", "-m", "Add a Latin-1 comment")
        latin1_sha = git(repo, "rev-parse", "HEAD")

        raw = subprocess.run(
            invoke_argv(repo, base_sha, latin1_sha),
            capture_output=True,
            check=False,
        )
        if raw.returncode != 0:
            failures.append(
                f"a non-UTF-8 diff byte exited {raw.returncode}: "
                f"{raw.stderr.decode('utf-8', 'replace').strip()}"
            )
        if b"/* caf\xe9 */" not in raw.stdout:
            failures.append("the non-UTF-8 diff byte did not survive into the block")

        fallback = invoke(repo, base_sha, head_sha, "--max-bytes", "1")
        command = f"git diff {base_sha}...{head_sha}"
        if fallback.returncode != 0:
            failures.append(f"fallback invocation exited {fallback.returncode}")
        if command not in fallback.stdout or "run `git diff" not in fallback.stdout:
            failures.append("fallback output does not tell the finder to run the pinned diff")
        if "+print('new')" in fallback.stdout:
            failures.append("fallback output still contains the oversized diff")
        if "emitted the command-based fallback" not in fallback.stderr:
            failures.append("fallback invocation did not print its stderr notice")

        failure = invoke(repo, base_sha, "not-a-commit")
        if failure.returncode != 2:
            failures.append(f"git failure exited {failure.returncode}, expected 2")
        if "git command failed:" not in failure.stderr or "not-a-commit" not in failure.stderr:
            failures.append("git failure does not identify the failing command")

    for failure in failures:
        print(failure)
    if failures:
        print(f"test_build_shared_block: {len(failures)} failure(s)")
        return 1
    print("test_build_shared_block: all cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
