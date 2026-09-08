# Review packet — `clap-rs/clap#6212` (target (clap-6212), issue #138 bounded discovery)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`clap-rs/clap#6212`](https://github.com/clap-rs/clap/pull/6212) — "Fix value_terminator has no effect when it is the first argument " |
| Author | `ericgumba` (association at fetch time: `CONTRIBUTOR`) |
| Repository URL (`summary.repository_url`) | `https://github.com/clap-rs/clap` |
| Head SHA | `3604b13117cbb652c10bb44b228b300d543dcc80` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `b9009a76d1f2d62ba6af168bcef12ad7272626ca` |
| Merge-base | `4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac` (**differs from the base SHA**: the base branch moved before the merge; review against the merge-base) |
| Diff | 2 files, +46 / −0, 2 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2026-01-27T20:18:05Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  clap_builder/src/parser/parser.rs                                      (+4    −0)
M  tests/builder/multiple_values.rs                                       (+42   −0)
```

## 3. Pull-request body, verbatim

```
Problem:
When -- is used as the first argument, a positional value_terminator should consume it and leave following values for the next positional. Instead, parsing switched to trailing values, causing the first positional to capture everything.

Solution:
Adjust escape handling so the current positional’s value_terminator takes precedence over entering trailing-values mode when it matches --.

Tests:

Added value_terminator_as_first_argument to cover the first-argument -- case.

#5040 
```

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `63d73bcf3` | 2026-01-26 | Eric Gumba | test(parser): Cover value_terminator as first argument<br><br>Adds a regression test for -- as the first argument terminating the<br>first positional and leaving following values for the next positional. |
| 2 | `3604b1311` | 2026-01-26 | Eric Gumba | fix(parser): Honor positional value_terminator<br><br>The value terminator should be able to consume --<br>even when it is the first argument, instead of forcing<br>trailing values.<br><br>Fixes #5040 |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2026-01-27T20:18:05Z` (the merge instant), reproduced verbatim

### Review submissions (11)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2026-01-07T16:14:59Z | `epage` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-07T16:15:28Z | `epage` | COMMENTED | `d2b03eef1` | *(empty)* |
| 2026-01-07T16:15:39Z | `epage` | COMMENTED | `d2b03eef1` | *(empty)* |
| 2026-01-07T16:18:28Z | `epage` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-09T14:07:37Z | `ericgumba` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-09T15:36:04Z | `epage` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-10T02:18:17Z | `ericgumba` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-10T02:20:34Z | `ericgumba` | COMMENTED | `1c1bd0c11` | *(empty)* |
| 2026-01-10T02:20:59Z | `ericgumba` | COMMENTED | `d2b03eef1` | *(empty)* |
| 2026-01-14T23:38:37Z | `epage` | COMMENTED | `9f7a28f31` | *(empty)* |
| 2026-01-27T04:57:31Z | `ericgumba` | COMMENTED | `9f7a28f31` | *(empty)* |

### Review threads (5), comments verbatim, in order

**1.** 2026-01-07T16:14:59Z · `epage` · `tests/builder/multiple_values.rs:1694` · on commit `1c1bd0c11` · thread resolved

```
Note that we [ask](https://github.com/clap-rs/clap/blob/master/CONTRIBUTING.md#preparing-the-pr) for all commits to be atomic which includes tests passing on every commit.  While we ask for the test be added first, it should be reproducing the bad behavior.
```

**2.** 2026-01-10T02:20:34Z · `ericgumba` · `tests/builder/multiple_values.rs:1694` · on commit `1c1bd0c11` · thread resolved

```
Reworked the commit history so that the test commit reproduces and asserts the bad behavior. The fix commit flips the testcase to the new correct behavior. 

At least that's what I got from reading through the PR history.
```

**3.** 2026-01-07T16:15:28Z · `epage` · `clap_builder/src/parser/parser.rs:143` · on commit `d2b03eef1` · thread resolved

```
Please follow the existing pattern of having a positive `if` with a comment inside of it explaining the case
```

**4.** 2026-01-10T02:20:59Z · `ericgumba` · `clap_builder/src/parser/parser.rs:143` · on commit `d2b03eef1` · thread resolved

```
Fixed
```

**5.** 2026-01-07T16:15:39Z · `epage` · `clap_builder/src/parser/parser.rs:140` · on commit `d2b03eef1` · thread resolved

```
Why `.map(|_| ())`?
```

**6.** 2026-01-07T16:18:28Z · `epage` · `tests/builder/multiple_values.rs:1662` · on commit `1c1bd0c11` · thread resolved

```
This test is specifically using an escape as a value separator and using it as the first argument for a positional.
```

**7.** 2026-01-09T14:07:37Z · `ericgumba` · `tests/builder/multiple_values.rs:1662` · on commit `1c1bd0c11` · thread resolved

```
I added some documentation to the testcase to add clarity.
```

**8.** 2026-01-09T15:36:03Z · `epage` · `tests/builder/multiple_values.rs:1662` · on commit `1c1bd0c11` · thread resolved

```
Better than documentation is clarifying the name of the test itself
```

**9.** 2026-01-10T02:18:16Z · `ericgumba` · `tests/builder/multiple_values.rs:1662` · on commit `1c1bd0c11` · thread resolved

```
Understood, I did both, let me know if there any additional issues.
```

**10.** 2026-01-14T23:38:36Z · `epage` · `tests/builder/multiple_values.rs:1662` · on commit `9f7a28f31` · thread resolved

````
While we have some, issue numbers are irrelevant for tests.  What matters here is that the value terminator is an escape value.

This is also saying it doesn't work but the next commit makes it work. 

maybe
```
fn escape_as_value_terminator_with_empty_list() {
```
````

**11.** 2026-01-27T04:57:31Z · `ericgumba` · `tests/builder/multiple_values.rs:1662` · on commit `9f7a28f31` · thread resolved

```
Thanks for the suggestion @epage. Fixed.
```

### Non-review conversation (1), verbatim, in order

**1.** 2026-01-27T20:18:00Z · `epage`

```
Thanks!
```

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | **yes** | `0e681f9ae28c7f2f90c4f0cc57b6a7a694319b30` |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | no | — |
| `.github/PULL_REQUEST_TEMPLATE.md` | **yes** | `0757758c8eb7bd553186eb86963ee856ae8f0840` |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 4a. User-supplied spec: `clap-rs/clap#5040`, verbatim, frozen at the cutoff `2026-01-27T20:18:05Z`

The pull-request body and its second commit message say `Fixes #5040`, but the forge's closing-reference query returned nothing for this pull request (the body carries the number without a closing keyword), so the builder's section 4 above records no originating issue. The orchestrator supplies the issue here as the user-supplied spec (`SKILL.md` step 1, order item 3). Record `issues=clap-rs/clap#5040` and `comments_available: true`. Title: **`value_terminator` has no effect when it is the first argument**, opened 2023-07-22 by `mamekoro` (https://github.com/clap-rs/clap/issues/5040).

Provenance, checked through the forge's edit metadata before inclusion: the issue body was last edited `2024-06-26T21:17:26Z`, before the cutoff, so the text below is the text that existed at the merge instant; comments first published after the cutoff, or edited after it, are omitted without being counted here, as the builder does for every other history route. Every included record is listed with its own timestamps.

| Record | Created | Last edited |
| --- | --- | --- |
| issue body | 2023-07-22T15:39:33Z | 2024-06-26T21:17:26Z |
| comment by `epage` | 2023-07-24T19:31:59Z | — |

````
### Please complete the following tasks

- [X] I have searched the [discussions](https://github.com/clap-rs/clap/discussions)
- [X] I have searched the [open](https://github.com/clap-rs/clap/issues) and [rejected](https://github.com/clap-rs/clap/issues?q=is%3Aissue+label%3AS-wont-fix+is%3Aclosed) issues

### Rust Version

rustc 1.71.0 (8ede3aae2 2023-07-12)

### Clap Version

4.3.19

### Minimal reproducible code

```rust
use clap::Parser;

#[derive(Clone, Debug, Parser)]
pub struct Args {
    #[arg(allow_hyphen_values = true, value_terminator = "--")]
    pub opts: Vec<String>,

    #[arg(allow_hyphen_values = true)]
    pub cmdline: Vec<String>,
}

fn main() {
    let args = Args::parse_from(["program", "--", "ls", "-l"]);
    println!("opts = {:?}, cmdline = {:?}", args.opts, args.cmdline);
}
```

`opts` is options for the program itself, and `cmdline` is arguments passed to an external program.

### Steps to reproduce the bug with the above code

```shell
cargo add clap --features derive
cargo run
```

### Actual Behaviour

It prints `opts = ["ls", "-l"], cmdline = []`

### Expected Behaviour

It should print `opts = [], cmdline = ["ls", "-l"]`

### Additional Context

This is related to https://github.com/clap-rs/clap/discussions/4960 and https://github.com/clap-rs/clap/pull/5037.

In addition to the reproduction above, I also tested the following code, all of them worked correctly.

`Args::parse_from(["program", "--name", "xyz", "--", "ls", "-l"])`
prints `opts = ["--name", "xyz"], cmdline = ["ls", "-l"]`

`Args::parse_from(["program", "--name", "xyz", "--"])`
prints `opts = ["--name", "xyz"], cmdline = []`

`Args::parse_from(["program", "--name", "xyz"])`
prints `opts = ["--name", "xyz"], cmdline = []`

`Args::parse_from(["program", "--"])`
prints `opts = [], cmdline = []`

`Args::parse_from(["program"])`
prints `opts = [], cmdline = []`


### Debug Output

<details>

```text
[clap_builder::builder::command]Command::_do_parse
[clap_builder::builder::command]Command::_build: name="test-clap-hyphen"
[clap_builder::builder::command]Command::_propagate:test-clap-hyphen
[clap_builder::builder::command]Command::_check_help_and_version:test-clap-hyphen expand_help_tree=false
[clap_builder::builder::command]Command::long_help_exists
[clap_builder::builder::command]Command::_check_help_and_version: Building default --help
[clap_builder::builder::command]Command::_propagate_global_args:test-clap-hyphen
[clap_builder::builder::debug_asserts]Command::_debug_asserts
[clap_builder::builder::debug_asserts]Arg::_debug_asserts:opts
[clap_builder::builder::debug_asserts]Arg::_debug_asserts:cmdline
[clap_builder::builder::debug_asserts]Arg::_debug_asserts:help
[clap_builder::builder::debug_asserts]Command::_verify_positionals
[clap_builder::parser::parser]Parser::get_matches_with
[clap_builder::parser::parser]Parser::get_matches_with: Begin parsing '"--"'
[clap_builder::parser::parser]Parser::possible_subcommand: arg=Ok("--")
[clap_builder::parser::parser]Parser::get_matches_with: sc=None
[clap_builder::parser::parser]Parser::get_matches_with: setting TrailingVals=true
[clap_builder::parser::parser]Parser::get_matches_with: Begin parsing '"ls"'
[clap_builder::parser::parser]Parser::get_matches_with: Positional counter...1
[clap_builder::parser::parser]Parser::get_matches_with: Low index multiples...true
[clap_builder::parser::parser]Parser::get_matches_with: Begin parsing '"-l"'
[clap_builder::parser::parser]Parser::get_matches_with: Positional counter...1
[clap_builder::parser::parser]Parser::get_matches_with: Low index multiples...true
[clap_builder::parser::parser]Parser::resolve_pending: id="opts"
[clap_builder::parser::parser]Parser::react action=Append, identifier=Some(Index), source=CommandLine
[clap_builder::parser::parser]Parser::remove_overrides: id="opts"
[clap_builder::parser::arg_matcher]ArgMatcher::start_custom_arg: id="opts", source=CommandLine
[clap_builder::builder::command]Command::groups_for_arg: id="opts"
[clap_builder::parser::arg_matcher]ArgMatcher::start_custom_arg: id="Args", source=CommandLine
[clap_builder::parser::parser]Parser::push_arg_values: ["ls", "-l"]
[clap_builder::parser::parser]Parser::add_single_val_to_arg: cur_idx:=1
[clap_builder::parser::parser]Parser::add_single_val_to_arg: cur_idx:=2
[clap_builder::parser::arg_matcher]ArgMatcher::needs_more_vals: o=opts, pending=0
[clap_builder::parser::arg_matcher]ArgMatcher::needs_more_vals: expected=1..=18446744073709551615, actual=0
[clap_builder::parser::parser]Parser::react not enough values passed in, leaving it to the validator to complain
[clap_builder::parser::parser]Parser::add_defaults
[clap_builder::parser::parser]Parser::add_defaults:iter:opts:
[clap_builder::parser::parser]Parser::add_default_value: doesn't have conditional defaults
[clap_builder::parser::parser]Parser::add_default_value:iter:opts: doesn't have default vals
[clap_builder::parser::parser]Parser::add_defaults:iter:cmdline:
[clap_builder::parser::parser]Parser::add_default_value: doesn't have conditional defaults
[clap_builder::parser::parser]Parser::add_default_value:iter:cmdline: doesn't have default vals
[clap_builder::parser::parser]Parser::add_defaults:iter:help:
[clap_builder::parser::parser]Parser::add_default_value: doesn't have conditional defaults
[clap_builder::parser::parser]Parser::add_default_value:iter:help: doesn't have default vals
[clap_builder::parser::validator]Validator::validate
[clap_builder::builder::command]Command::groups_for_arg: id="opts"
[clap_builder::parser::validator]Conflicts::gather_direct_conflicts id="opts", conflicts=[]
[clap_builder::parser::validator]Conflicts::gather_direct_conflicts id="Args", conflicts=[]
[clap_builder::parser::validator]Validator::validate_conflicts
[clap_builder::parser::validator]Validator::validate_exclusive
[clap_builder::parser::validator]Validator::validate_conflicts::iter: id="opts"
[clap_builder::parser::validator]Conflicts::gather_conflicts: arg="opts"
[clap_builder::parser::validator]Conflicts::gather_conflicts: conflicts=[]
[clap_builder::parser::validator]Validator::validate_required: required=ChildGraph([])
[clap_builder::parser::validator]Validator::gather_requires
[clap_builder::parser::validator]Validator::gather_requires:iter:"opts"
[clap_builder::parser::validator]Validator::gather_requires:iter:"Args"
[clap_builder::parser::validator]Validator::gather_requires:iter:"Args":group
[clap_builder::parser::validator]Validator::validate_required: is_exclusive_present=false
[clap_builder::parser::arg_matcher]ArgMatcher::get_global_values: global_arg_vec=[]
opts = ["ls", "-l"], cmdline = []
```

</details>
````

### Issue comments through the frozen cutoff, verbatim, in order (1 total; `comments_available: true`)

**1.** 2023-07-24T19:31:59Z · `epage`

```
Huh, I know I tested for this case.  I guess I didn't pay close enough attention to the result
```

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **Execution allowance.** Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 item 2 states: run cargo from the clone root with CARGO_HOME=/tmp/bd148/cargo-home CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=<your work dir>/target, for example `cargo test --offline --locked --test builder <name filter>` (about 30 seconds to build the test binary, then the filtered tests run in under a second); five minutes per command; a filter at most once per flag set; scratch crates only under your work directory; nothing added to or changed in the clone. The registry cache is already populated and no network call of any kind is available. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `3604b1311`. Nothing that happened after this pull request exists locally. Do not try to work
   around this. At the end, report explicitly whether you read any history beyond the pinned head and
   which history commands you ran.
4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
   anything anywhere. Follow your skill through to the point where it would publish, then render the
   review **exactly as it would be posted**, including summary body (with the `Mode` line your
   contract requires for a merged target), per-finding comments, and any trailers, and stop.
5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
   triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
   tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "<the model your dispatch names for that worker>"`
   explicitly on every call**.
6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
   any verifier or finder: the manifest and requirement ledger when they are complete, then the
   complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
   they arrive. A session interruption after that point loses nothing that the file holds.
7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
   own report and payload paths only. Do not read any other run's clone, report, or payload. Report
   it if you read one anyway.
