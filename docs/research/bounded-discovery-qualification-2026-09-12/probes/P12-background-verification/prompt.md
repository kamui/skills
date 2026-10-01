Answer with exactly the three lines below, in order, and nothing else. No preamble, no summary.

1. A line starting `BACKGROUND: ` — dispatch the sub-agent named `bd-verifier` exactly once with the task `Write one short paragraph about the history of the printing press, then end with the single word DONEBG.` and with background execution requested (`run_in_background: true`). Write `requested` here if the tool accepted a background dispatch, or the refusal text verbatim if it did not.
2. A line starting `SHELL: ` — while the sub-agent is still running, use the shell tool once to run exactly `python3 -c "print(6*7)"` and put its output here.
3. A line starting `CHILD: ` — collect the sub-agent's result and put its final word here.

Do nothing else.
