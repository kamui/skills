# Removed guarantees and unchanged code — issue #161

Instruction replay for [#161](https://github.com/kamui/skills/issues/161), part of
[#156](https://github.com/kamui/skills/issues/156). The pre-change rule text is pinned at
`ab3c9b05b5b6724c673da1c4d5845ea740338117` (`v2b-1`); the implementation advances
`code-audit-publish` to `v2b-2`.

**What this is.** Each case below is a focused source fixture traced by hand through the
pre-change and post-change instruction text, to show which rule admits or refuses it and on what
evidence. It is a paper transition check of the rules, and nothing more.

**What this is not.** No reviewer was run against these fixtures, on either revision. There is no
corpus, no attempt count, no adjudicated recovery, and no rescoring of any historical snapshot.
These replays therefore measure no recall or precision gain, and the release claims none: a rule
that admits a class of defect is not evidence that a finder will find one, and a fixture built to
exercise a rule is not evidence about unseen pull requests. What they do establish is that the
intended admissions pass the new gate, that the intended refusals still fail it, and that the two
rules this release was required to preserve still decide their own cases.

## The rule change being traced

| Owner | `v2b-1` | `v2b-2` |
| --- | --- | --- |
| `references/code-axis.md` | Criterion 4 excludes "pre-existing issues, including real ones on lines the change did not modify"; the only exception is § Sync drift from a changed rule, which is documentary. | Criterion 4 names two shapes of introduction; new § Guarantees removed from unchanged code admits a consumer whose relied-on guarantee the diff removed or weakened, on a four-part comparison, and keeps an already-unsafe base path out. |
| `references/verify.md` | `pre-existing` refutation: "the defect is real but this change did not introduce it. Cite the prior state." | Same bullet plus § The pre-existing comparison: four steps against both revisions, and an unreconstructable base state rules `plausible` rather than `refuted`. |
| `references/finding-format.md` | Anchor ladder rung 2: "the diff line that **makes the finding true**". | Same ladder plus its removed-guarantee case: anchor at the line that removed the protection, `fix` at the untouched consumer, and an explicit prohibition on presenting the consumer's line as one the diff touches. |

## Case 1 — a removed lock races an unchanged reader

Fixture. `snapshot` is byte-identical across the revisions; only `put` is in the diff.

```python
# cache.py — base
class Cache:
    def __init__(self):
        self._lock = threading.Lock()
        self._entries = {}

    def put(self, key, value):
        with self._lock:              # base guarantee: every mutation under _lock
            self._entries[key] = value

    def snapshot(self):
        with self._lock:
            return dict(self._entries)
```

```diff
     def put(self, key, value):
-        with self._lock:
-            self._entries[key] = value
+        self._entries[key] = value    # dict assignment is atomic
```

`snapshot` still takes `_lock`, but `_lock` no longer excludes writers, so its copy can run while
`put` inserts.

**`v2b-1`:** refused twice. Criterion 4 puts `snapshot` out of scope because the diff did not
modify its lines, and the one exception is documentary. A finder that raised it anyway reaches a
`pre-existing` refutation whose whole requirement — "cite the prior state" — is satisfied by
observing that `snapshot` is unchanged at base, which is the same reasoning that excluded it.

**`v2b-2`:** the guarantee shape, with all four parts quotable — base `cache.py:8` `with
self._lock:` guaranteeing every mutation under `_lock`; head `cache.py:8` writing outside it;
consumer `cache.py:12` `return dict(self._entries)`; trigger a `put` concurrent with a `snapshot`,
raising `RuntimeError: dictionary changed size during iteration`. The candidate is admitted with
both revisions and the consumer in its `claim`. At the verifier, step 4 of the comparison fails —
the guarantee was stronger at base — so `pre-existing` is unavailable and the claim is ruled on its
own evidence. Whether that ruling is `confirmed` or `plausible` remains the verifier's judgment
about the trigger; the replay establishes only that neither gate now removes the candidate
silently. Anchor at the head `put` line, `fix=cache.py:12`.

## Case 2 — the same path was already unsafe at base

Fixture. Same file, but the lock-free write predates the pull request, which only adds logging.

```python
# cache.py — base
    def put(self, key, value):
        self._entries[key] = value    # already unlocked at base
```

```diff
     def put(self, key, value):
+        log.debug("put %s", key)
         self._entries[key] = value
```

**`v2b-1`:** out of scope by criterion 4, and `pre-existing` at the verifier.

**`v2b-2`:** unchanged, and now for a stated reason. The finder runs its own trigger against the
base and gets the same `RuntimeError`, so the section sends it to an acquitted ledger row. The
verifier's step 4 holds — the guarantee was no stronger at base — so `pre-existing` is the correct
refutation and it is reached by comparison rather than by noticing that `snapshot` is untouched.
The widened admission does not pull old bugs into scope.

## Case 3 — a refactor that preserves the guarantee

Fixture. The mutation moves; the lock moves with it.

```diff
     def put(self, key, value):
-        with self._lock:
-            self._entries[key] = value
+        self._store(key, value)
+
+    def _store(self, key, value):
+        with self._lock:
+            self._entries[key] = value
```

**`v2b-1`:** nothing admitted.

**`v2b-2`:** still nothing. Part 2 of the comparison has nothing to quote — every mutation is still
under `_lock` at head — so the guarantee shape does not open, and the section refuses the
substitutes a finder might reach for instead: "That the diff touches the function, that it is a
large refactor, that the new code is harder to follow, that some caller *might* have depended on
something — none of those is a candidate." The strict reading of criterion 4 is restated in the
same release, so re-exposure by rewriting is still not introduction.

## Case 4 — a required re-export missing from an untouched `__init__.py`

Fixture. The issue requires `RetryPolicy` to be importable from the package root. The diff adds
`pkg/retry.py` defining it and never touches `pkg/__init__.py`, which is unchanged and re-exports
only the older names.

**`v2b-1`:** admitted. The Requirements axis measures against the issue, and `verify.md`'s
`pre-existing` bullet is marked **Code candidates only** with the reason stated in place.

**`v2b-2`:** admitted, by the same two sentences, kept verbatim. This is the case the release was
required not to break, because a general introduction rule is exactly what could erode it:
`code-axis.md` § Guarantees removed from unchanged code now says in its own text that it is a
Code-axis rule and that an explicit unmet obligation is this change's responsibility even when the
missing work lives entirely in unchanged code, and `verify.md` § The pre-existing comparison sits
under a bullet that still refuses the refutation for Requirements candidates outright. The
candidate's `fix` is `pkg/__init__.py`; since that file has no diff line, the anchor comes from
rung 2 or 3 at the `pkg/retry.py` line that makes the gap true, or from the review body — not from
a fabricated coordinate in `__init__.py`.

## Case 5 — old/new documentation peer drift

Fixture. A canonical reference retires a closed list in favour of an open rule; an untouched
sibling skill file still restates the retired list.

**`v2b-1`:** admitted by § Sync drift from a changed rule, on its own evidence rule — establish the
peer set, sweep each changed contract repository-wide twice (once for the new vocabulary, once for
a short distinctive fragment of the retired wording), inspect every live result, and record each in
the ledger.

**`v2b-2`:** admitted by the same section, with the same two searches and the same ledger
obligation. The new section names sync drift as the documentary case of the same base/head question
and points at it; it does not absorb it. The distinction is load-bearing: a stale doc peer has no
lock, ordering, ownership rule or validated invariant to quote, so the four-part comparison would
refuse a real drift if it replaced the paired sweep. Priority and action still come from
`finding-format.md`'s restatement calibration, which caps restatement drift at `P2`.

## Limits

- Five hand-built fixtures, each written to exercise one rule. They are not sampled from real pull
  requests and carry no distributional claim.
- Nothing here measures whether a finder *reaches* the guarantee — discovery is the concern of
  [#157](https://github.com/kamui/skills/issues/157), and this release only changes what is
  admitted once reached.
- Cases 1 and 2 turn on CPython dict semantics chosen to make the trigger concrete. The rule is not
  language-specific, and no other language was replayed.
- Case 1's final verdict is deliberately left open: the release removes two silent exclusions, and
  a `confirmed`/`plausible` split on a real run is a model judgment this document cannot settle.
