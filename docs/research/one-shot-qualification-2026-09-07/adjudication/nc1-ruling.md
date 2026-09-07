# Adjudication: FAQ.md line 135 `$ source <(rg --generate complete-zsh)` claim

## 1. Is the text accurate?

Full passage as it exists at head (`855bfa6`), `FAQ.md` lines 91–150:

```
<h3 name="complete">
Does ripgrep have support for shell auto-completion?
</h3>

Yes! If you installed ripgrep through a package manager on a Unix system, then
the shell completion files included in the release archive should have been
installed for you automatically. If not, you can generate completions using
ripgrep's command line interface.

For **bash**:

```
$ dir="$XDG_CONFIG_HOME/bash_completion"
$ mkdir -p "$dir"
$ rg --generate complete-bash > "$dir/rg.bash"
```

For **fish**:

```
$ dir="$XDG_CONFIG_HOME/fish/completions"
$ mkdir -p "$dir"
$ rg --generate complete-fish > "$dir/rg.fish"
```

For **zsh**, the recommended approach is:

```zsh
$ dir="$HOME/.zsh-complete"
$ mkdir -p "$dir"
$ rg --generate complete-zsh > "$dir/_rg"
```

And then add `$HOME/.zsh-complete` to your `fpath` in, e.g., your
`$HOME/.zshrc` file:

```zsh
fpath=($HOME/.zsh-complete $fpath)
```

Or if you'd prefer to load and generate completions at the same time, you can
add the following to your `$HOME/.zshrc` file:

```zsh
$ source <(rg --generate complete-zsh)
```

Note though that while this approach is easier to setup, is generally slower
than the previous method, and will add more time to loading your shell prompt.

For **PowerShell**, create the completions:
...
```

The prose is unambiguous: "**add the following to your `$HOME/.zshrc` file**" immediately precedes the block containing `$ source <(rg --generate complete-zsh)`. This is not framed as a one-time terminal command ("run this now") — it is explicitly framed as file content to be appended to `.zshrc`, exactly parallel to the sentence one paragraph above it ("add `$HOME/.zsh-complete` to your `fpath` in ... your `$HOME/.zshrc` file"), whose accompanying block (`fpath=($HOME/.zsh-complete $fpath)`) correctly has no prompt prefix. So yes: the prose instructs the reader to paste that exact line, `$ ` included, into `.zshrc`.

## 2. What is the file's own convention?

I read every fenced block in `FAQ.md` at head (68 code fences / 34 blocks). Two convention classes matter:

**A. Blocks explicitly introduced as "add ... to your `<config/profile file>`":**

| Lines | Content | Has `$ ` prompt prefix? |
|---|---|---|
| 127–129 | `fpath=($HOME/.zsh-complete $fpath)` (added to `.zshrc`) | **No** |
| 134–136 | `$ source <(rg --generate complete-zsh)` (added to `.zshrc`) | **Yes** ← disputed line |
| 347–353 | PowerShell `$OrigFgColor` / `Reset-ForegroundColor` function (added to PowerShell profile) | **No** |

Within this narrow, most-relevant class, 2 of 3 instances (including the block *immediately preceding* the disputed one, added by the very same section of this same PR) omit the `$ ` prefix, consistent with the fact that these lines are meant to be pasted verbatim into a config file, not typed at a prompt. The disputed line is the lone outlier, and it breaks convention against its own immediate neighbor.

**B. Blocks showing one-time terminal commands (not file content):** these are inconsistent in the file as a whole. Multi-command "transcript" style blocks that also show captured output almost always use `$ ` (e.g. lines 70–74, 102–106, 110–114, 118–122, 143–145, 217–223, 228–231, 291–297, 320–328, 504–507, 547–552, 564–578, 586–601, 615–622, 636–651, 658–672, 695–709, 721–735). But several later single-command examples omit the prefix despite being commands to run, not file content: line 433–441 (`rg --colors ... foo`), 873–875 (`rg foo --files-with-matches`), 884–886, 898–900, 911–913 (all `sed`/`xargs` examples). So the broad "command vs. file-content" split is not perfectly rigid across the whole document — I note this because the task asks me to flag inconsistency, and it does weaken any claim that `$ ` is an infallible file-wide signal of "type this, don't paste it into a file." However, the narrower and more directly relevant convention — blocks explicitly framed as "add this to your rc/profile file" never carry `$ `, including the one right next to the disputed line — is clean and directly contradicted only by the disputed line.

## 3. Does it actually fail?

Reproduced with the system zsh (`zsh 5.9`, Homebrew `rg 15.2.0`):

```
$ cat /tmp/qual137/test.zshrc
$ source <(rg --generate complete-zsh)

$ zsh -c 'source /tmp/qual137/test.zshrc'
/tmp/qual137/test.zshrc:1: command not found: $
exit: 127
```

And simulating a real interactive shell startup with this as `.zshrc` (via `ZDOTDIR`):

```
$ ZDOTDIR=/tmp/qual137/zdotdir_broken zsh -i -c 'echo done' </dev/null
/tmp/qual137/zdotdir_broken/.zshrc:2: command not found: $
done
```

Every interactive shell start prints `command not found: $` to stderr and the `source` call is never reached, so completions are never loaded by this method — the shell does otherwise still start (not a hard crash of the session), but the exact feature this line exists to enable (dynamic zsh-completion loading) never happens.

Control: stripping the stray `$ ` (line content `source <(rg --generate complete-zsh)`) and pre-loading `compinit` (a normal precondition for zsh completion, satisfied in any zsh setup that already has completion enabled) sources cleanly:

```
$ zsh -c 'autoload -Uz compinit && compinit -u; source /tmp/qual137/test2.zshrc; echo "sourced OK, exit=$?"'
sourced OK, exit=0
```

This isolates the `$ ` prefix, specifically, as the cause of the failure — not some other defect in the generated completion script or the `source <(...)` idiom itself.

Merge-base check: this whole "For **zsh**, the recommended approach is:" ... "Or if you'd prefer to load and generate completions at the same time" passage, including the disputed block, does not exist at the merge-base at all (see §4) — at merge-base, the zsh section is just the three-line `dir=`/`mkdir`/`rg --generate` block with no `.zshrc`-paste instructions whatsoever, so there is no earlier version of this passage to compare a "does it fail" question against.

## 4. Was the line introduced by this PR?

Yes, unambiguously. `git diff 79cbe89..855bfa6 -- FAQ.md`:

```diff
-For **zsh**:
+For **zsh**, the recommended approach is:

-```
+```zsh
 $ dir="$HOME/.zsh-complete"
 $ mkdir -p "$dir"
 $ rg --generate complete-zsh > "$dir/_rg"
 ```

+And then add `$HOME/.zsh-complete` to your `fpath` in, e.g., your
+`$HOME/.zshrc` file:
+
+```zsh
+fpath=($HOME/.zsh-complete $fpath)
+```
+
+Or if you'd prefer to load and generate completions at the same time, you can
+add the following to your `$HOME/.zshrc` file:
+
+```zsh
+$ source <(rg --generate complete-zsh)
+```
+
+Note though that while this approach is easier to setup, is generally slower
+than the previous method, and will add more time to loading your shell prompt.
+
 For **PowerShell**, create the completions:
```

The entire `fpath=`/`source <(...)` sub-passage, including the disputed `$ source <(rg --generate complete-zsh)` line, is new content added by this PR (across its two commits `7c2a7b0` and `855bfa6`, both squashed into the merged head). It did not exist at the merge-base under any form.

## 5. Consequence

If a reader follows the literal instruction ("add the following to your `$HOME/.zshrc` file") and pastes `$ source <(rg --generate complete-zsh)` verbatim:

- Every new interactive zsh session prints `command not found: $` to stderr at startup (demonstrated above).
- The intended `source` never executes, so this PR's headline feature — dynamically sourcing zsh completions without a separate generation step — silently never activates; only the loud, unrelated-looking error is the symptom, not an explanation of the missing completions.
- The failure is loud (an error every shell start) but not deeply informative — many users, especially those less familiar with the `$ ` shell-prompt convention (this section is explicitly a beginner-facing "how do I set this up" FAQ), would need to notice the error, realize it correlates with something they just pasted into `.zshrc`, and go find and strip the stray character. This is a real but modest debugging step — self-correctable by anyone who knows `$ ` is a prompt marker, but not obvious to everyone the doc is aimed at, and it is objectively true that copy-pasting the block exactly as instructed breaks shell startup and defeats the documented feature.
- It's not a security, data-integrity, or silent-corruption issue, and recovery is one character-deletion once noticed — so this sits toward the lower-severity end of "material," but it is a genuine, demonstrated, reproducible functional break of the exact thing the PR was written to document, triggered by literally following the PR's own instructions.

## 6. Counter-arguments

- **"`$ ` is a universally understood prompt marker that readers strip automatically."** Partially accepted as mitigating severity (many experienced users will indeed recognize and strip it, or immediately diagnose the startup error), but not accepted as making the claim false or the defect nonexistent: the prose's own instruction is to "add the following" — an explicit, literal copy-paste directive, not "run the following" or "type the following at your prompt." The document itself distinguishes between these two framings in the very same section (contrast "the recommended approach is [terminal steps]" with "add the following to your `.zshrc` file" for both the `fpath=` and `source <(...)` blocks), and the `fpath=` block correctly omits the prefix while the disputed one — same instruction verb, same target file, two paragraphs later — does not. That the reader *could* recover by knowing a convention doesn't mean the artifact as shipped is correct.
- **"The block may be intended as a terminal command, not file content."** Rejected: the prose sentence immediately preceding it is unambiguous and structurally identical to the preceding `fpath=` example. There is no reading under which "add the following to your `$HOME/.zshrc` file" means "type this once at your prompt and don't save it."
- **"Documentation-only issues fall below the material bar."** This is the strongest counter and I take it seriously, but the task's own material-defect definition includes "explicit-requirement failure with a demonstrated consequence," and I have demonstrated, by direct reproduction, that following the PR's explicit, literal instruction breaks interactive shell startup with a loud error and prevents the documented feature from working at all. That's a functional consequence, not a typo, phrasing awkwardness, or stylistic nit — the distinguishing bar the task asks me to apply against "cosmetic or stylistic complaint." I do weigh the easy self-correctability and the localized blast radius (one FAQ code block, one alternate/optional method explicitly described as the slower, non-recommended alternative) as reasons to keep this at the low end of material rather than treating it as severe.

## Ruling

MATERIAL — GT-n1

**Trigger:** Following FAQ.md's explicit instruction ("add the following to your `$HOME/.zshrc` file") and pasting the code block at (head) FAQ.md line 135, `$ source <(rg --generate complete-zsh)`, verbatim into `.zshrc`.

**Demonstrated consequence:** Every interactive zsh startup emits `command not found: $` (reproduced via `zsh -i` with the block installed as `.zshrc`, exit code 127 on direct sourcing) and the `source` call is never reached, so the zsh completions this PR's "load and generate completions at the same time" method exists to provide are never loaded — the alternate installation method this PR introduces is non-functional exactly as instructed. Isolated by a control run showing the identical line minus the stray `$ ` sources cleanly (with `compinit` preloaded, a normal precondition of any zsh completion setup).

**Required corrective outcome:** Remove the stray `$ ` shell-prompt prefix from the `.zshrc`-paste block (i.e., the block should read `source <(rg --generate complete-zsh)`), consistent with the file's own convention for "add this to your rc/profile file" blocks (e.g. the adjacent `fpath=($HOME/.zsh-complete $fpath)` block and the PowerShell profile-function block), so that a reader who copies the documented snippet into `.zshrc` gets a working `source` call rather than a `command not found: $` error at every shell startup.
