#!/usr/bin/env python3
"""Exercise the phase-1 packet builder through the build_packet.py CLI.

Usage: python3 docs/research/tools/test_build_packet.py
Inputs: the saved GraphQL response in test_build_packet_fixture.json, small saved REST bodies
for the two optional reference fetches, and a temporary git mirror built per test. No network:
every forge call is replayed through --replay.
Exit codes: 0 all checks pass; 1 a test fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("build_packet.py")
FIXTURE = Path(__file__).with_name("test_build_packet_fixture.json")

CUTOFF = "2026-03-10T12:00:00Z"

# a double quote forces git to quote the path whatever core.quotePath is set to, and is ASCII, so
# the fixture does not depend on how the filesystem normalises non-ASCII names
QUOTED_DIRECTORY = 'docs/q"dir'


REF_PR = {
    "title": "Retry ceiling, first attempt",
    "body": "Superseded by the reviewed pull request.",
    "created_at": "2026-02-20T09:00:00Z",
    "user": {"login": "carol"},
    "state": "closed",
    "merged": False,
    "closed_at": "2026-03-10T12:00:05Z",
}
REF_PR_COMMENTS = [
    {"user": {"login": "alice"}, "created_at": "2026-02-21T09:00:00Z", "body": "Closing in favour of the bounded loop."},
    {"user": {"login": "dana"}, "created_at": "2026-03-16T09:00:00Z", "body": "Post-merge note that must not reach the packet."},
]
SPEC_ISSUE = {
    "html_url": "https://github.com/other/spec/issues/12",
    "title": "Reconnect must give up",
    "body": "The client must stop retrying after a bounded number of attempts.",
    "created_at": "2026-02-10T09:00:00Z",
    "user": {"login": "erin"},
}
SPEC_ISSUE_COMMENTS = [
    {"user": {"login": "erin"}, "created_at": "2026-02-11T09:00:00Z", "body": "A ceiling of five attempts is enough."},
    {"user": {"login": "dana"}, "created_at": "2026-03-17T09:00:00Z", "body": "Post-merge note that must not reach the packet."},
]


class BuildPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.mirror = self.directory / "mirror"
        self.replay = self.directory / "replay"
        self.replay.mkdir()
        self.out = self.directory / "packets" / "a" / "packet.md"
        self.merge_base, self.head = self.build_mirror()
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.fixture["data"]["repository"]["pullRequest"]["headRefOid"] = self.head

    # --- fixtures -------------------------------------------------------

    def git(self, *args: str, when: str = "2026-03-07T07:00:00+00:00") -> str:
        environment = {
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(self.directory),
            "GIT_AUTHOR_NAME": "Bob", "GIT_AUTHOR_EMAIL": "bob@example.com",
            "GIT_COMMITTER_NAME": "Bob", "GIT_COMMITTER_EMAIL": "bob@example.com",
            "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
        }
        done = subprocess.run(["git", "-C", str(self.mirror), *args], check=True,
                              capture_output=True, text=True, encoding="utf-8", env=environment)
        return done.stdout.strip()

    def build_mirror(self) -> tuple:
        """A two-commit repository standing in for the staging mirror."""
        self.mirror.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.mirror)], check=True, capture_output=True)
        self.write(self.mirror / "AGENTS.md", "Root guidance.\n")
        self.write(self.mirror / "src" / "AGENTS.md", "Scoped guidance for src/.\n")
        self.write(self.mirror / "src" / "retry.rs", "fn retry() { loop {} }\n")
        self.write(self.mirror / "docs" / "notes.md", "Notes.\n")
        self.write(self.mirror / QUOTED_DIRECTORY / "AGENTS.md", "Scoped guidance for a quoted path.\n")
        self.write(self.mirror / QUOTED_DIRECTORY / "a.md", "A file git prints quoted.\n")
        self.write(self.mirror / "guide" / "AGENTS.md", "Scoped guidance for guide/.\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Base of the reviewed change")
        base = self.git("rev-parse", "HEAD")
        self.write(self.mirror / "src" / "retry.rs", "fn retry() { for _ in 0..5 {} }\n")
        self.write(self.mirror / "src" / "lib.rs", "pub mod retry;\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Bound the reconnect retry loop", when="2026-03-09T07:00:00+00:00")
        head = self.git("rev-parse", "HEAD")
        return base, head

    def touch_the_quoted_path(self) -> None:
        """Add a commit changing the file under the quoted directory, and repin the head to it."""
        self.write(self.mirror / QUOTED_DIRECTORY / "a.md", "A file git prints quoted, changed.\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Touch the quoted path", when="2026-03-09T08:00:00+00:00")
        self.head = self.git("rev-parse", "HEAD")
        self.fixture["data"]["repository"]["pullRequest"]["headRefOid"] = self.head

    def rename_into_guide(self) -> None:
        """Add a commit renaming docs/notes.md into guide/, and repin the head to it."""
        self.git("mv", "docs/notes.md", "guide/notes.md")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Move the notes under guide/", when="2026-03-09T08:00:00+00:00")
        self.head = self.git("rev-parse", "HEAD")
        self.fixture["data"]["repository"]["pullRequest"]["headRefOid"] = self.head

    @staticmethod
    def write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def drop_the_closing_reference(self) -> None:
        """Leave the pull request with no closing issue, connection count included."""
        references = self.fixture["data"]["repository"]["pullRequest"]["closingIssuesReferences"]
        references["nodes"], references["totalCount"] = [], 0

    def save_replay(self, **bodies) -> None:
        """Save the forge responses this run replays; the GraphQL body defaults to the fixture."""
        bodies.setdefault("graphql", self.fixture)
        for name, body in bodies.items():
            path = self.replay / (name.replace("_", "-") + ".json")
            path.write_text(json.dumps(body), encoding="utf-8")

    def run_cli(self, *options: str, save: bool = True) -> subprocess.CompletedProcess:
        if save:
            self.save_replay()
        arguments = [
            sys.executable, str(SCRIPT),
            "--repo", "example/retry", "--pr", "3952",
            "--head", self.head, "--merge-base", self.merge_base, "--base-sha", self.merge_base,
            "--staging", str(self.mirror), "--target", "a",
            "--replay", str(self.replay), "--out", str(self.out),
        ]
        return subprocess.run([*arguments, *options], capture_output=True, text=True, encoding="utf-8")

    def build_ok(self, *options: str, save: bool = True) -> str:
        result = self.run_cli(*options, save=save)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.out.read_text(encoding="utf-8")

    # --- the cutoff -----------------------------------------------------

    def test_default_cutoff_is_the_merge_instant(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"cutoff {CUTOFF}; omitted after cutoff: "
                      "{'reviews': 1, 'thread_comments': 2, 'conversation': 1, 'issue_comments': 1}",
                      result.stdout)
        self.assertIn("2 reviews, 2 thread comments, 1 conversation comments, 1 issues", result.stdout)

    def test_material_after_the_cutoff_is_omitted(self) -> None:
        packet = self.build_ok()
        for kept in ["The retry loop needs a bound, not a longer sleep.",
                     "Bound this loop.",
                     "Bounded in the follow-up commit.",
                     "Opening for review; the ceiling is configurable.",
                     "Reproduced on 1.2.0 with a proxy that closes mid-handshake."]:
            self.assertIn(kept, packet)
        for omitted in ["downstream breakage report",
                        "Still spinning in production after the merge.",
                        "Filed #4001 for the fallout.",
                        "Reverted in #4002.",
                        "Reopening: the shipped fix still hot-loops"]:
            self.assertNotIn(omitted, packet)

    def test_a_thread_emptied_by_the_cutoff_is_dropped(self) -> None:
        packet = self.build_ok()
        self.assertIn("### Review threads (1), comments verbatim, in order", packet)
        self.assertNotIn("src/lib.rs:7", packet)

    def test_the_packet_states_the_cutoff_and_not_the_omitted_count(self) -> None:
        packet = self.build_ok()
        self.assertIn(f"## 6. Prior review state through the frozen cutoff `{CUTOFF}` (the merge instant)", packet)
        self.assertIn(f"### Issue comments through the frozen cutoff `{CUTOFF}`", packet)
        self.assertNotIn("omitted", packet.lower())

    def test_an_explicit_earlier_cutoff_drops_more(self) -> None:
        earlier = "2026-03-08T09:30:00Z"
        result = self.run_cli("--cutoff", earlier)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"cutoff {earlier}; omitted after cutoff: "
                      "{'reviews': 2, 'thread_comments': 3, 'conversation': 1, 'issue_comments': 1}",
                      result.stdout)
        packet = self.out.read_text(encoding="utf-8")
        self.assertIn(f"## 6. Prior review state through the frozen cutoff `{earlier}`, reproduced verbatim", packet)
        self.assertNotIn("Bounded in the follow-up commit.", packet)

    def test_the_pinned_merge_instant_survives_an_earlier_cutoff(self) -> None:
        packet = self.build_ok("--cutoff", "2026-03-08T09:30:00Z")
        self.assertIn("| `merged` | **`true`** (merged 2026-03-10T12:00:00Z) |", packet)

    def test_a_comment_whose_review_was_submitted_after_the_cutoff_is_omitted(self) -> None:
        thread = self.fixture["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"][0]
        thread["comments"]["nodes"][1]["pullRequestReview"] = {"submittedAt": "2026-03-11T09:00:00Z"}
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("'thread_comments': 3", result.stdout)
        self.assertNotIn("Bounded in the follow-up commit.", self.out.read_text(encoding="utf-8"))

    def test_a_standalone_thread_comment_within_the_cutoff_is_kept(self) -> None:
        packet = self.build_ok()
        self.assertIn("Bounded in the follow-up commit.", packet)

    def test_material_edited_after_the_cutoff_is_omitted(self) -> None:
        pull = self.fixture["data"]["repository"]["pullRequest"]
        pull["reviews"]["nodes"][0]["lastEditedAt"] = "2026-03-11T09:00:00Z"
        pull["reviewThreads"]["nodes"][0]["comments"]["nodes"][1]["lastEditedAt"] = "2026-03-11T09:00:00Z"
        pull["comments"]["nodes"][0]["lastEditedAt"] = "2026-03-11T09:00:00Z"
        pull["closingIssuesReferences"]["nodes"][0]["comments"]["nodes"][0]["lastEditedAt"] = "2026-03-11T09:00:00Z"
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("omitted after cutoff: "
                      "{'reviews': 2, 'thread_comments': 3, 'conversation': 2, 'issue_comments': 2}",
                      result.stdout)
        packet = self.out.read_text(encoding="utf-8")
        for edited in ["The retry loop needs a bound, not a longer sleep.",
                       "Bounded in the follow-up commit.",
                       "Opening for review; the ceiling is configurable.",
                       "Reproduced on 1.2.0 with a proxy that closes mid-handshake."]:
            self.assertNotIn(edited, packet)

    def test_material_edited_before_the_cutoff_is_kept(self) -> None:
        pull = self.fixture["data"]["repository"]["pullRequest"]
        pull["reviews"]["nodes"][0]["lastEditedAt"] = "2026-03-08T09:30:00Z"
        packet = self.build_ok()
        self.assertIn("The retry loop needs a bound, not a longer sleep.", packet)

    def test_a_rest_comment_updated_after_the_cutoff_is_omitted(self) -> None:
        self.drop_the_closing_reference()
        comments = [dict(REF_PR_COMMENTS[0], updated_at="2026-03-16T09:00:00Z")]
        self.save_replay(ref_pr=REF_PR, ref_pr_comments=comments)
        packet = self.build_ok("--ref-pr", "3899", save=False)
        self.assertNotIn("Closing in favour of the bounded loop.", packet)
        self.assertIn("(0 total; `comments_available: true`)", packet)

    def test_a_quoted_post_cutoff_instant_fails_the_scan(self) -> None:
        issue = self.fixture["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]
        issue["comments"]["nodes"][0]["body"] = "Reproduced; the failing run is at 2026-03-20T09:00:00Z."
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"2026-03-20T09:00:00Z is later than the cutoff {CUTOFF}", result.stdout)
        self.assertIn("not written: 1 instant(s) after the cutoff", result.stdout)
        self.assertFalse(self.out.exists())

    def test_a_quoted_basic_format_offset_fails_the_scan(self) -> None:
        issue = self.fixture["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"][0]
        issue["comments"]["nodes"][0]["body"] = "Reproduced; the failing run is at 2026-03-20T09:00:00+0530."
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"2026-03-20T09:00:00+0530 is later than the cutoff {CUTOFF}", result.stdout)
        self.assertFalse(self.out.exists())

    # --- the mirror -----------------------------------------------------

    def test_the_manifest_and_commits_come_from_the_mirror(self) -> None:
        packet = self.build_ok()
        self.assertIn("A  src/lib.rs", packet)
        self.assertIn("M  src/retry.rs", packet)
        self.assertIn("| Diff | 2 files, +2 / −1, 1 commits |", packet)
        self.assertIn(f"| 1 | `{self.head[:9]}` | 2026-03-09 | Bob | Bound the reconnect retry loop |", packet)

    def test_a_rename_names_real_paths_in_the_manifest_and_the_guidance_scope(self) -> None:
        self.rename_into_guide()
        packet = self.build_ok()
        self.assertIn("D  docs/notes.md", packet)
        self.assertIn("A  guide/notes.md", packet)
        self.assertNotIn("=>", packet)
        self.assertIn("| `guide/AGENTS.md` | **yes** |", packet)

    def test_a_path_git_would_quote_reaches_the_manifest_and_the_guidance_scope_raw(self) -> None:
        self.touch_the_quoted_path()
        packet = self.build_ok()
        self.assertIn(f"M  {QUOTED_DIRECTORY}/a.md", packet)
        self.assertIn(f"| `{QUOTED_DIRECTORY}/AGENTS.md` | **yes** |", packet)
        self.assertNotIn('\\"', packet)

    def test_guidance_at_the_merge_base_covers_root_and_scoped_files(self) -> None:
        packet = self.build_ok()
        self.assertIn("| `AGENTS.md` | **yes** |", packet)
        self.assertIn("| `CLAUDE.md` | no | — |", packet)
        self.assertIn("| `src/AGENTS.md` | **yes** |", packet)
        self.assertNotIn("| `src/CLAUDE.md` |", packet)

    # --- the optional sections -----------------------------------------

    def test_an_originating_pull_request_reference_renders_as_the_spec(self) -> None:
        self.drop_the_closing_reference()
        self.save_replay(ref_pr=REF_PR, ref_pr_comments=REF_PR_COMMENTS)
        packet = self.build_ok("--ref-pr", "3899", save=False)
        self.assertIn("## 4. Originating reference `#3899` (a pull request, closed unmerged), verbatim", packet)
        self.assertIn("Closing in favour of the bounded loop.", packet)
        self.assertNotIn("Post-merge note that must not reach the packet.", packet)
        self.assertIn("closed 2026-03-10T12:00:05Z when the reviewed pull request merged.", packet)

    def test_a_cross_repository_spec_issue_renders_as_the_spec(self) -> None:
        self.drop_the_closing_reference()
        self.save_replay(spec_issue=SPEC_ISSUE, spec_issue_comments=SPEC_ISSUE_COMMENTS)
        packet = self.build_ok("--spec-issue", "other/spec#12", save=False)
        self.assertIn("## 4. User-supplied spec: `other/spec#12`, verbatim", packet)
        self.assertIn("A ceiling of five attempts is enough.", packet)
        self.assertNotIn("Post-merge note that must not reach the packet.", packet)

    def test_a_pull_request_with_no_reference_says_so(self) -> None:
        self.drop_the_closing_reference()
        packet = self.build_ok()
        self.assertIn("## 4. Originating issue\n\nNone.", packet)

    def test_the_extra_section_lands_before_the_run_conditions(self) -> None:
        extra = self.directory / "extra.md"
        extra.write_text("## 7b. Upstream material\n\nSee `upstream/`.\n", encoding="utf-8")
        packet = self.build_ok("--extra-section", str(extra))
        self.assertLess(packet.index("## 7b. Upstream material"), packet.index("## 8. Run conditions"))

    def test_publish_to_fork_switches_the_run_conditions(self) -> None:
        packet = self.build_ok("--publish-to-fork")
        self.assertIn("**Publication is ENABLED**", packet)
        self.assertNotIn("**Publication is disabled.**", packet)
        self.assertIn("publication is ENABLED**", packet)

    def test_the_program_strings_default_to_the_124_experiment(self) -> None:
        packet = self.build_ok("--publish-to-fork")
        self.assertIn("(target (a), issue #124 effort experiment)", packet)
        self.assertIn("the original author is `scop`", packet)
        self.assertIn("no access to `spf13/cobra`", packet)
        self.assertIn('**pass `model: "sonnet"` explicitly on every call**', packet)

    def test_another_program_states_its_own_label_and_identities(self) -> None:
        packet = self.build_ok("--publish-to-fork",
                               "--experiment-label", "issue #137 recall grid",
                               "--subagent-model", "opus",
                               "--upstream-repo", "example/upstream",
                               "--original-author", "frank")
        self.assertIn("(target (a), issue #137 recall grid)", packet)
        self.assertIn("the original author is `frank`", packet)
        self.assertIn("no access to `example/upstream`", packet)
        self.assertIn('**pass `model: "opus"` explicitly on every call**', packet)
        for stale in ["issue #124 effort experiment", "`scop`", "spf13/cobra", 'model: "sonnet"']:
            self.assertNotIn(stale, packet)

    def test_the_execution_note_reaches_the_run_conditions(self) -> None:
        packet = self.build_ok("--execution-note", "Focused tests only, five minutes each.")
        self.assertIn("Focused tests only, five minutes each.", packet)

    # --- refusals -------------------------------------------------------

    def test_a_head_mismatch_exits_two(self) -> None:
        self.fixture["data"]["repository"]["pullRequest"]["headRefOid"] = "0" * 40
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("head mismatch", result.stderr)
        self.assertFalse(self.out.exists())

    def test_a_missing_replay_response_exits_two(self) -> None:
        result = self.run_cli(save=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)

    def test_an_unmerged_pull_request_without_a_cutoff_exits_two(self) -> None:
        pull = self.fixture["data"]["repository"]["pullRequest"]
        pull["merged"], pull["mergedAt"], pull["state"] = False, None, "OPEN"
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("no --cutoff and the pull request is not merged", result.stderr)

    def test_an_unmerged_pull_request_builds_with_a_cutoff(self) -> None:
        pull = self.fixture["data"]["repository"]["pullRequest"]
        pull["merged"], pull["mergedAt"], pull["state"] = False, None, "OPEN"
        packet = self.build_ok("--cutoff", CUTOFF)
        self.assertIn("| `merged` | **`false`** (not merged) |", packet)
        self.assertNotIn("merged None", packet)
        self.assertIn("the target is not merged and this run does not publish", packet)
        self.assertIn("The target is not merged; this review is frozen at the cutoff.", packet)
        self.assertNotIn("The target is merged; this is a retrospective review.", packet)
        self.assertIn(f"## 6. Prior review state through the frozen cutoff `{CUTOFF}`, reproduced verbatim", packet)

    def test_a_truncated_connection_exits_two(self) -> None:
        pull = self.fixture["data"]["repository"]["pullRequest"]
        pull["reviews"]["totalCount"] = 101
        pull["reviewThreads"]["nodes"][0]["comments"]["totalCount"] = 50
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("the single forge query truncated reviews (3 of 101); "
                      "comments on the src/retry.rs:42 thread (3 of 50)", result.stderr)
        self.assertFalse(self.out.exists())

    def test_a_complete_connection_does_not_exit_two(self) -> None:
        packet = self.build_ok()
        self.assertIn("### Review submissions (2)", packet)

    def test_a_malformed_cutoff_exits_two(self) -> None:
        result = self.run_cli("--cutoff", "last tuesday")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not an ISO-8601 instant", result.stderr)

    def test_an_unreadable_extra_section_exits_two(self) -> None:
        result = self.run_cli("--extra-section", str(self.directory / "absent.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)

    def test_a_staging_mirror_without_the_pinned_shas_exits_two(self) -> None:
        empty = self.directory / "empty"
        empty.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(empty)], check=True, capture_output=True)
        self.save_replay()
        result = self.run_cli("--staging", str(empty), save=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("command failed: git", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
