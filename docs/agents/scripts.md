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

## Invocation from `SKILL.md`

Write the command as `python3 scripts/<name>.py …` with the path relative to the skill root, so it works without an executable bit. Say what the agent does on a non-zero exit: report the script's output and stop the step. The fix is to the script, and the script's output is what the next step consumes.

## Declaring the requirement

A skill that ships scripts declares it in `SKILL.md` frontmatter with the Agent Skills `compatibility` field:

```yaml
compatibility: Requires git and Python 3.9+ on macOS or Linux
```
