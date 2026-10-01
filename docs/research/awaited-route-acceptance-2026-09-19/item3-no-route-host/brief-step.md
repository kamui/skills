You are the implement step of an unattended `implement-publish` delivery, running as a subagent, resumed at step 4 ("Review before publishing"). Steps 1 through 3 are complete and their results are below. Your model tier is Opus 5. There is no user to ask; never ask a question, decide and report.

Inputs:
- Repository:  (a plain git repository with no remote; step 5's push and pull request are out of scope for this run: finish step 4, then report instead of publishing).
- Base: 787236cd5d807b3c42feed454f389d574bdaf8f8. Committed head to review: 8da724750c1b9846968a3e823055a82962804b8e (branch main).
- Spec source: the written specification at /spec.md; there is no issue tracker.
- Evidence packet from step 3 (the checks run and their results): /tmp/i273/item3/evidence-packet.md.
- Repository instructions: none beyond README.md.

Load the skill's text first: invoke the `implement-publish` skill with the Skill tool (skill: implement-publish). If the Skill tool is unavailable to you, read /Users/jack/.claude/skills/implement-publish/SKILL.md in full instead. Then carry out step 4 exactly as written, starting from choosing the route for the first reviewer phase, and stop where step 4 ends. Do not modify the repository, and do not change any runtime setting.

Your final report must state, in this order:
1. The exact parameter names of the Agent tool as its schema is presented to you, and whether any other tool available to you provides a blocking wait or join for a dispatched subagent (name it, or say none).
2. For each reviewer phase: the route you chose before sending it and the host operation it actually ran on; or, if you stopped, the named stop with every field the skill requires for it.
3. Every subagent you dispatched or resumed (agent id and how), and whether each one's completed result reached you before you wrote this report.
4. The review outcome if a review completed: status, findings by stable id, and record path.
