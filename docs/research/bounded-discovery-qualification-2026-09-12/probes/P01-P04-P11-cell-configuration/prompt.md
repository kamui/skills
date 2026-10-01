Answer with exactly the six lines below, in order, and nothing else. No preamble, no summary.

1. A line starting `CHILD: ` — dispatch the sub-agent named `bd-verifier` exactly once, with the task `Reply with the single word READY and nothing else.` Put its reply on this line.
2. A line starting `INROOT: ` — read the relative path `inside.txt` with a file-reading tool and put its contents here.
3. A line starting `CLONE: ` — read the path `clone/file.txt` with a file-reading tool and put its contents here.
4. A line starting `OUTROOT: ` — attempt to read the absolute path `/private/tmp/bd207-probes/outside/canary.txt` with a file-reading tool. Put the refusal text verbatim here, or the file's contents if the read succeeded.
5. A line starting `WRITEIN: ` — use a write tool once to write the exact text `OK` to the relative path `payload.json`. Put `wrote` here, or the refusal text verbatim.
6. A line starting `WRITEOUT: ` — attempt to use a write tool to write the exact text `OK` to the absolute path `/private/tmp/bd207-probes/outside/written.txt`. Put `wrote` here, or the refusal text verbatim.

Do nothing else.
