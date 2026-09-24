# Review packet — `BurntSushi/ripgrep#2957` (target (n), issue #137 qualification grid)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`BurntSushi/ripgrep#2957`](https://github.com/BurntSushi/ripgrep/pull/2957) — "feat(completion): support sourcing zsh completion dynamically" |
| Author | `vegerot` (association at fetch time: `CONTRIBUTOR`) |
| Repository URL (`summary.repository_url`) | `https://github.com/BurntSushi/ripgrep` |
| Head SHA | `855bfa6cdae4f4fe8762f892fc4957635397083e` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `79cbe89deb1151e703f4d91b19af9cdcc128b765` |
| Merge-base | `79cbe89deb1151e703f4d91b19af9cdcc128b765` (identical to the base SHA) |
| Diff | 2 files, +29 / −4, 2 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2024-12-31T13:23:13Z) |
| `isDraft` | `false` |
| Originating issue(s) | [`BurntSushi/ripgrep#2956`](https://github.com/BurntSushi/ripgrep/issues/2956) — "Can't source zsh completions directly" (closing reference in the PR body) |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  FAQ.md                                                                 (+20   −3)
M  crates/core/flags/complete/rg.zsh                                      (+9    −1)
```

## 3. Pull-request body, verbatim

````
Summary:
Previously, you needed to save the completion script to a file and then
source it.  Now, you can dynamically source completions in zsh by
running

```zsh
$ source <(rg --generate complete-zsh)
```

Test plan:
1. Run `source <(rg --generate complete-zsh)`
2. Run `rg --generate=complete-zs<TAB>`

Before this commit, you would get an error after step 1.
After this commit, it should work as expected.

Closes #2956
````

## 4. Originating issue `BurntSushi/ripgrep#2956`, verbatim

Title: **Can't source zsh completions directly**  
Opened 2024-12-30 by `vegerot`.

````
#### Describe your feature request

The way I load many completions is by sourcing them in my `.zshrc`, for example

```zsh
  if type fzf > /dev/null; then
	  source <(fzf --zsh)
  fi

  if type gh > /dev/null; then
	source <(TCELL_MINIMIZE=1 gh completion -s zsh)
  fi

  if type fd > /dev/null; then
	  source <(fd --gen-completions)
  fi
```

However, this doesn't work for ripgrep.  If I run `rg --generate=complete-zsh`, I get

```zsh
$ source <(rg --generate=complete-zsh)

_arguments:comparguments:327: can only be called from completion function
```

As a workaround, I can put `rg --generate=complete-zsh > /somewhere/in/fpath/_rg` and it works, but I'm hoping to avoid that
````

### Issue comments through the frozen cutoff `2024-12-31T13:23:13Z`, verbatim, in order (0 total; `comments_available: true`)

*(none)*

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `7c2a7b018` | 2024-12-30 | Max 👨🏽‍💻 Coplan | feat(completion): support sourcing zsh completion dynamically<br><br>Summary:<br>Previously, you needed to save the completion script to a file and then<br>source it.  Now, you can dynamically source completions in zsh by<br>running<br><br>```zsh<br>$ source <(rg --generate complete-zsh)<br>```<br><br>Test plan:<br>1. Run `source <(rg --generate complete-zsh)`<br>2. Run `rg --generate=complete-zs<TAB>`<br><br>Before this commit, you would get an error after step 1.<br>After this commit, it should work as expected.<br><br>Closes #2956 |
| 2 | `855bfa6cd` | 2024-12-31 | Andrew Gallant | improve FAQ text for zsh completions |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2024-12-31T13:23:13Z` (the merge instant), reproduced verbatim

### Review submissions (10)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2024-12-31T00:06:43Z | `BurntSushi` | COMMENTED | `1b2871720` | r? @okdana  |
| 2024-12-31T00:22:21Z | `vegerot` | COMMENTED | `1b2871720` | *(empty)* |
| 2024-12-31T00:26:22Z | `vegerot` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T00:42:57Z | `okdana` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T00:45:31Z | `okdana` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T00:51:30Z | `okdana` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T00:57:17Z | `vegerot` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T01:01:22Z | `vegerot` | COMMENTED | `a7de1f8ed` | *(empty)* |
| 2024-12-31T01:57:36Z | `vegerot` | COMMENTED | `1b2871720` | *(empty)* |
| 2024-12-31T01:58:32Z | `vegerot` | COMMENTED | `1b2871720` | *(empty)* |

### Review threads (3), comments verbatim, in order

**1.** 2024-12-31T00:06:19Z · `BurntSushi` · `FAQ.md:128` · on commit `1b2871720` · thread resolved

```
Why are we suggesting this method? I'm okay with supporting it as long as it doesn't have any costs to doing so, but I don't see a good reason to specifically highlight it in the docs.
```

**2.** 2024-12-31T00:22:21Z · `vegerot` · `FAQ.md:128` · on commit `1b2871720` · thread resolved

````
Personal preference.  I personally like doing it this way because it makes installation easier.  Since the generation is fast, I don't need to think about installing `_rg` and can just put in my zshrc

```zsh
  if type rg > /dev/null; then
	  eval "$(rg --generate=complete-zsh)"
  fi
```

I assume other people prefer it this way too, which is why projects like [fzf](https://github.com/junegunn/fzf?tab=readme-ov-file#setting-up-shell-integration) suggest it by default.  That is why I suggested it in the doc.

If you disagree, then I can remove this bit 🙂 
````

**3.** 2024-12-31T00:51:30Z · `okdana` · `FAQ.md:128` · on commit `1b2871720` · thread resolved

```
i don't know for sure but i'd guess that other projects suggest this `source` method just because it's self-contained and it works regardless of whatever else might be in the user's zsh profile. creating a personal directory for completion functions and adding it to `fpath` is more idiomatic, more extensible, and (as the comment here mentions) faster at start-up, but harder to explain. i don't have a strong opinion on whether they should both be mentioned in the faq

eta: another benefit is that the function is self-updating. maybe that's a more compelling reason
```

**4.** 2024-12-31T01:57:36Z · `vegerot` · `FAQ.md:128` · on commit `1b2871720` · thread resolved

```
Based on how difficult it is to explain (see other thread), I think it makes more sense to show new users the easiest method by default, and if they want the more "idiomatic" / performant (slightly) option we can show it as an alternative.  The FAQ is going to be read by people who may not want to create directories, new files, and update their fpath.
```

**5.** 2024-12-31T01:58:31Z · `vegerot` · `FAQ.md:128` · on commit `1b2871720` · thread resolved

```
@okdana @BurntSushi how about I remove the FAQ patch, and we can discuss how to improve the FAQ in a new issue? (continued from https://github.com/BurntSushi/ripgrep/pull/2957#discussion_r1899864739 )
```

**6.** 2024-12-31T00:26:22Z · `vegerot` · `crates/core/flags/complete/rg.zsh:438` · on commit `a7de1f8ed` · thread resolved

````
I originally wrote this as 

```zsh
if [[ "$funcstack[1]" = "_rg" ]]; then
  _rg "$@"
elif type compdef >/dev/null; then
    compdef _rg rg
fi
```

But `ci/test-complete` didn't like that.  ~~I feel like the test is wrong~~ (nvm I am wrong!), because realistically you will either have `compdef` or will run the completion as `_rg`.  I stared at the test for a few seconds and didn't want to spend more time digging into it.  Instead, I worked around it by making it


```zsh
if [[ "$funcstack[1]" = "_rg" ]]; then
  _rg "$@"
elif type compdef >/dev/null; then
    compdef _rg rg
else
  _rg "$@"
fi
```

To be clear, this code is fine, but feels redundant 🤷🏼‍♀️
````

**7.** 2024-12-31T00:42:57Z · `okdana` · `crates/core/flags/complete/rg.zsh:438` · on commit `a7de1f8ed` · thread resolved

````
the test script isn't wrong. the function is designed to be sourced by it without requiring anything from the completion system. we could have the script load `compdef` but it would still do the wrong thing with that check. i would suggest this as more idiomatic (and faster) than the `type` method:

```zsh
if [[ $funcstack[1] == _rg ]] || (( ! $+functions[compdef] )); then
```
````

**8.** 2024-12-31T01:01:21Z · `vegerot` · `crates/core/flags/complete/rg.zsh:438` · on commit `a7de1f8ed` · thread resolved

```
Thanks! Done
```

**9.** 2024-12-31T00:45:31Z · `okdana` · `FAQ.md:122` · on commit `a7de1f8ed` · thread resolved

```
obv this is a pre-existing issue but these instructions don't really do anything as written. i would suggest we add something like 'then add `$dir` to your `fpath`'. if you'd rather not do this here i can make another pr
```

**10.** 2024-12-31T00:57:17Z · `vegerot` · `FAQ.md:122` · on commit `a7de1f8ed` · thread resolved

````
I can do that.

...orr, we could suggest the easier way I'm adding in this commit.

> If you installed ripgrep with a package manager, you should have shell completions automatically (Brew users see [here](https://docs.brew.sh/Shell-Completion))
> However, if completions aren't working, then add to your `zshrc`
> ```zsh
> source <(rg --generate=complete-zsh)
> ```

I like the idea of hoping their package manager does the right thing, but if doesn't then suggesting a simple one-liner instead of a multi-step process of creating directories, files, and adding things to your `fpath`.  On my machine (granted, it's over $1k) it only adds 4ms of overhead which is acceptable imo.
````

### Non-review conversation (1), verbatim, in order

**1.** 2024-12-31T13:11:11Z · `BurntSushi`

```
I've left it in the FAQ and fixed up the wording by adding an appropriate caveat emptor. I guess since other projects have found it useful to suggest this method it's probably not too big of a deal for ripgrep to do it too. But the text now makes it clear that the "generate and source" approach is slower. 4ms might not seem like much, and indeed, I cannot perceive a 4ms lag, but if you accrue 10 of those kinds of things, it starts to pile up into something that is noticeable.
```

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | no | — |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | no | — |
| `.github/PULL_REQUEST_TEMPLATE.md` | no | — |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **Execution allowance.** Focused execution IS permitted on this target, offline and outside the clone: zsh is installed and you may write and run scratch zsh scripts under your work directory to check the behaviour of shell code you have read. Five minutes per command. Building the Rust crate is NOT available (no network, no vendored registry) — do not attempt cargo build or cargo test. Nothing may be added to or changed in the clone. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `855bfa6cd`. Nothing that happened after this pull request exists locally. Do not try to work
   around this. At the end, report explicitly whether you read any history beyond the pinned head and
   which history commands you ran.
4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
   anything anywhere. Follow your skill through to the point where it would publish, then render the
   review **exactly as it would be posted**, including summary body (with the `Mode` line your
   contract requires for a merged target), per-finding comments, and any trailers, and stop.
5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
   triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
   tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "sonnet"`
   explicitly on every call**.
6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
   any verifier or finder: the manifest and requirement ledger when they are complete, then the
   complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
   they arrive. A session interruption after that point loses nothing that the file holds.
7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
   own report and payload paths only. Do not read any other run's clone, report, or payload. Report
   it if you read one anyway.
