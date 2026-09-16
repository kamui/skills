# Scripts

Conventions for executable code under a skill's `scripts/` directory and for the repo's own tooling under `scripts/`.

## Platforms

macOS and Linux, including WSL. Native Windows is out of scope: nothing here is written or tested for it. Git is required everywhere, and on both supported platforms a working `git` implies a working `python3`.

## Language

Skill scripts are Python, standard library only, running on Python 3.9 and newer. Repo tooling that installs or syncs skills is POSIX `sh`.

Why this and not a compiled language or a JavaScript runtime:

- The runtime is already present wherever `git` is. A compiled language would trade that for a build toolchain on every host or per-platform binaries committed to git.
- The agent writes, runs, and repairs these scripts. Stdlib Python is the language it does that most reliably in, and the one a non-Python reader can still follow.
- A script's wall clock is the `git` subprocesses it wraps. Interpreter speed does not register against the minutes of model time the script replaces.

## Division of labour

A script does mechanical work: builds a prompt, validates a payload, hashes context, parses a fenced block. Every review judgment stays in the model: which candidate is real, what its status is, whether two are duplicates. Where a script's check and the reference text disagree, the reference text wins and the script is what gets fixed.

## Each script

- Opens with `#!/usr/bin/env python3`, a module docstring giving purpose, usage, exit codes, and input schema, then `from __future__ import annotations`.
- Parses arguments with `argparse`. Input arrives as arguments, stdin, or the local git repository; forge calls (`gh`) stay in `SKILL.md` steps.
- Passes `encoding="utf-8"` to every `open()` and to `subprocess.run(..., text=True)`.
- Exits `0` on success, `1` on a content violation with one line per violation on stdout, `2` when input cannot be read or a subprocess fails, naming the failing command on stderr.
- Ships a `--self-test` flag or a `test_<name>.py` sibling that drives it through `subprocess`, so exit codes are what gets tested. Run it before committing.

`review-code/scripts/review_context.py --worktree` writes unreferenced loose objects and a temporary index without changing the real index, refs, or working files; configured clean filters run, including on untracked files, and retain their normal side effects.

## `review-bot` departures

`review-bot/scripts/review_token.py` mints a GitHub App installation token, which the conventions above do not anticipate. It departs from them in three recorded ways:

- It runs `openssl dgst -sha256 -sign <key>` as a subprocess for the RS256 JWT signature. The standard library has no RSA, so the skill declares `openssl` in place of `git` in its `compatibility` field.
- It makes its own forge HTTPS calls through `urllib.request` instead of leaving forge calls to `gh` in `SKILL.md` steps: a JWT is not a `gh` credential. `curl` is not used, so no dependency is added. A TLS verification failure exits 2 with a one-line hint naming `Install Certificates.command` and `SSL_CERT_FILE`.
- Its stdout carries only the token, and every failure reason, exit 1 or 2, goes to stderr. Consumers capture stdout as the token and discard it on failure, so a reason on stdout would be swallowed.

A dependent reaches this script only through the review-token command returned by `review-bot`, which names the installed skill's own absolute path; no dependent writes a path to it.

## Invocation from `SKILL.md`

Write the command as `python3 scripts/<name>.py …` with the path relative to the skill root, so it works without an executable bit. Say what the agent does on a non-zero exit: report the script's output and stop the step. The fix is to the script, and the script's output is what the next step consumes.

The named install-alone exception is `review-code-publish` and `implement-publish` requiring `review-code`; other skills remain independent. A skill that runs another skill's script uses the absolute path named in the returned record, never a sibling-relative path.

## Declaring the requirement

A skill that ships scripts declares it in `SKILL.md` frontmatter with the Agent Skills `compatibility` field:

```yaml
compatibility: Requires git and Python 3.9+ on macOS or Linux
```
