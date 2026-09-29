# Run document — holdout target (c), cell `panel-seed1`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/c/packet.md`, SHA-256 `5e0e80d3d8d74e40c5b4cacb7e12b9d37b7ccc5d10857c653629e527b444036d` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `a8c82c5766bcc9f5d` / `a8c82c5766bcc9f5d` |
| Payload | [`panel-seed1-payload.md`](panel-seed1-payload.md), 25458 bytes |
| Report (this file, below the preamble) | 106155 bytes as written by the reviewer |
| Closed out | 2026-09-04T22:30:26.084804+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `a8c82c5766bcc9f5d` | primary | general-purpose | `claude-sonnet-5`×157 | `high`×157 | `agent-a8c82c5766bcc9f5d.jsonl` |
| `a0eab4fadeececefb` | child | general-purpose | `claude-sonnet-5`×6 | `high`×6 | `agent-a0eab4fadeececefb.jsonl` |
| `a1d994452b89e60a7` | child | general-purpose | `claude-sonnet-5`×59 | `high`×59 | `agent-a1d994452b89e60a7.jsonl` |
| `aa4f1803aa23027ca` | child | general-purpose | `claude-sonnet-5`×63 | `high`×63 | `agent-aa4f1803aa23027ca.jsonl` |
| `a160554b1feb065d7` | child | general-purpose | `claude-sonnet-5`×148 | `high`×148 | `agent-a160554b1feb065d7.jsonl` |
| `ae24e10364cb33747` | child | general-purpose | `claude-sonnet-5`×2 | `high`×2 | `agent-ae24e10364cb33747.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-a8c82c5766bcc9f5d.jsonl
turns                        79 (API requests; 157 assistant lines)
tool calls                   84
text-only turns               1
input                       158 tokens (uncached)
cache write             764,550 tokens
cache read           13,769,480 tokens
output                  129,842 tokens (thinking 34,597)
models             claude-sonnet-5
wall                    0:50:20
cost                       5.96 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a0eab4fadeececefb.jsonl
turns                         3 (API requests; 6 assistant lines)
tool calls                    3
text-only turns               1
input                         6 tokens (uncached)
cache write              17,022 tokens
cache read               51,333 tokens
output                    8,336 tokens (thinking 689)
models             claude-sonnet-5
wall                    0:01:00
cost                       0.14 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a1d994452b89e60a7.jsonl
turns                        23 (API requests; 59 assistant lines)
tool calls                   35
text-only turns               1
input                        46 tokens (uncached)
cache write              53,766 tokens
cache read              919,553 tokens
output                   26,615 tokens (thinking 17,505)
models             claude-sonnet-5
wall                    0:05:04
cost                       0.58 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-aa4f1803aa23027ca.jsonl
turns                        27 (API requests; 63 assistant lines)
tool calls                   35
text-only turns               1
input                        54 tokens (uncached)
cache write              86,701 tokens
cache read            1,617,657 tokens
output                   18,222 tokens (thinking 11,492)
models             claude-sonnet-5
wall                    0:05:22
cost                       0.72 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a160554b1feb065d7.jsonl
turns                        74 (API requests; 148 assistant lines)
tool calls                   74
text-only turns               1
input                       148 tokens (uncached)
cache write             168,712 tokens
cache read            7,975,369 tokens
output                   74,692 tokens (thinking 48,533)
models             claude-sonnet-5
wall                    0:14:51
cost                       2.76 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-ae24e10364cb33747.jsonl
turns                         1 (API requests; 2 assistant lines)
tool calls                    0
text-only turns               1
input                         2 tokens (uncached)
cache write              11,341 tokens
cache read                7,021 tokens
output                    5,026 tokens (thinking 377)
models             claude-sonnet-5
wall                    0:00:32
cost                       0.08 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                       207 (API requests; 435 assistant lines)
tool calls                  231
text-only turns               6
input                       414 tokens (uncached)
cache write           1,102,092 tokens
cache read           24,340,413 tokens
output                  262,733 tokens (thinking 113,193)
models             claude-sonnet-5
wall                    1:17:09 (summed over transcripts)
cost                      10.25 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          9.99 $ (output 236,194 after subtracting the report's 26,539 est. tokens)
```

Row for `comparison-data.md`:

| (c) panel seed 1 | claude-sonnet-5 | 207 | 231 | 6 | 414 | 1,102,092 | 24,340,413 | 262,733 | 113,193 | 1:17:09 | 10.25 | 26,539 | **9.99** |

Per agent:

| primary a8c82c5766bcc9f5d | claude-sonnet-5 | 79 | 84 | 1 | 158 | 764,550 | 13,769,480 | 129,842 | 34,597 | 0:50:20 | 5.96 | — | — |
| child a0eab4fadeececefb | claude-sonnet-5 | 3 | 3 | 1 | 6 | 17,022 | 51,333 | 8,336 | 689 | 0:01:00 | 0.14 | — | — |
| child a1d994452b89e60a7 | claude-sonnet-5 | 23 | 35 | 1 | 46 | 53,766 | 919,553 | 26,615 | 17,505 | 0:05:04 | 0.58 | — | — |
| child aa4f1803aa23027ca | claude-sonnet-5 | 27 | 35 | 1 | 54 | 86,701 | 1,617,657 | 18,222 | 11,492 | 0:05:22 | 0.72 | — | — |
| child a160554b1feb065d7 | claude-sonnet-5 | 74 | 74 | 1 | 148 | 168,712 | 7,975,369 | 74,692 | 48,533 | 0:14:51 | 2.76 | — | — |
| child ae24e10364cb33747 | claude-sonnet-5 | 1 | 0 | 1 | 2 | 11,341 | 7,021 | 5,026 | 377 | 0:00:32 | 0.08 | — | — |

---

# Run report — target (c) `python/typeshed#9458`, arm v2a (Panel line), seed 1

Skill: `code-review-deep-publish`, pinned at `snapshot-path-omitted dd3bcfe (workflow=v2a-1 with #53-#58 merged)`, read from `/tmp/holdout/skills/panel/`.

Model: `claude-sonnet-5` for the reviewer (this context) and for every sub-agent (`model: "sonnet"` passed explicitly on every `Agent` call — see § Every sub-agent dispatch for verbatim confirmation from each transcript).

Wall clock: started reading the dispatch and skill snapshot; timestamps not separately logged by the harness beyond this report's own construction order. See § Notes for the approximate breakdown.

## 1. Metadata

- **Target:** `python/typeshed#9458` — "Bump redis to 4.4.0", merged 2023-01-05T15:25:11Z.
- **Arm:** v2a (Panel line, with merged fixes #53–#58) — `code-review-deep-publish`.
- **Seed:** 1.
- **Skill pin:** `snapshot-path-omitted dd3bcfe`.
- **Run identity:** base ref `main`, base SHA (pinned run identity used throughout) `8365b1aaefd46d506ca0dfe73e9721da2d03c566` (= merge-base; the base SHA as recorded on the PR, `70025c372346288675437fc0bd273db84cc0b3d5`, is not reachable in this truncated clone and the packet directs review against the merge-base), head SHA `55dfb451101480275ae05f2f08d1a899a691a77d`, merge-base `8365b1aaefd46d506ca0dfe73e9721da2d03c566`. Repository canonical web URL: `https://github.com/python/typeshed`.
- **Originating reference:** `python/typeshed#9329` ("[stubsabot] Bump redis to 4.4.0"), a closed, unmerged pull request that this PR's body closes with `Closes #9329`; per the packet, treated as the originating issue text (spec source). `issues=python/typeshed#9329`.
- **Posting identity:** `kamui`, did not author the PR, no prior comments/reviews on it → ordinary first review by a third party, event `COMMENT`. Target is merged → retrospective review, publication disabled.
- **"context digest":** the Panel skill (`code-review-deep-publish`, its `SKILL.md` and all `references/*.md`) defines no "context" digest concept anywhere — confirmed by an exhaustive case-insensitive `grep -rn -i "digest"` over `/tmp/holdout/skills/panel/`, zero hits. That concept belongs to a different skill (`legacy reviewer`), not this one. Treated as inapplicable to this dispatch's rule 3 and noted under § Notes as a judgment call. The closest analog this skill actually specifies is the **pinned run identity** (base, head, merge-base triple), computed once above from the packet and the clone, and reused verbatim in every script invocation and every sub-agent prompt (see § Every sub-agent dispatch).
- **Sub-agents spawned:** 3 roles, 5 `Agent` calls total — Code finder (1 initial dispatch + 1 shape-fix re-dispatch), Requirements finder (1 initial dispatch + 1 shape-fix re-dispatch), Verifier (1, no re-dispatch needed). All `model: "sonnet"`, all in the foreground, all run sequentially, one after another, each fully awaited before the next was dispatched. See § 4 for every dispatch's exact prompt and verbatim report.
- **Verification trigger:** the mandatory fresh-context verifier is unconditional in this skill (not trigger-gated) — it runs whenever either finder returns at least one candidate. Both finders returned candidates, so the verifier ran (see § 7 below and § Mechanism checklist).
- **Candidates raised / surviving:** Code finder raised 1 candidate (`code/asyncio-connection-pyi/missing-can-read-destructive`) + 1 observation, over a 14-row ledger. Requirements finder raised 8 candidates + 1 question (`requirements/submodule-interface-parity-undecidable`, from its "cannot tell from the code" bucket) + 2 observations, over an 18-row ledger. Verifier ruled on all 9 candidates that reached it (the question does not go to the verifier, per `verify.md`'s "one class of item never goes to the verifier"): **9 confirmed, 0 plausible, 0 refuted**; 1 merge (Code's candidate collapsed into the matching Requirements candidate, id `requirements/asyncio-can-read-destructive`, per verify.md § Deduplicate's "keep the Requirements one" rule), yielding **8 surviving distinct findings**. I independently spot-checked 5 of the 9 confirmations (`replace_default_node`, `get_retry`/`set_retry`, `MaxConnectionsError`, `get_message`'s `Optional[float]` widening, `can_read_destructive` presence in the stub) directly against the upstream trees and the stub file myself — see § 4.3 and § 10 — and all held up.
- **Findings for publication:** 8 (3 `must-fix`, 5 `consider`, all axis `Requirements` after the merge) — see § 2 and the payload at `/tmp/holdout/reports/c/panel-seed1-payload.md`.
- **Questions:** 1 total — the Requirements "cannot tell" question about six submodules' upstream parity. (The verifier returned **zero** `plausible` verdicts, so no additional question came from that channel; an earlier draft of this metadata section, written before the verifier ran, anticipated one and was wrong — corrected here once the verifier's actual result was known.)
- **Observations:** 3 published (at the publishing.md cap of 3), 0 dropped. Pooled from: Code's 1 observation (`credentials.pyi` `@abstractmethod` on a non-ABC class), Requirements' 2 observations (the same `@abstractmethod` fact, and `asyncio/lock.pyi`'s `Redis[Any]` narrowing), and the verifier's 2 observations (`sentinel.pyi`'s `type: ignore[override]`, and a self-referential note about my own anchor placement on two candidates). I deduplicated the two `@abstractmethod` observations (same fact, `credentials.pyi:3` vs `:4`) to one, and did **not** publish the verifier's anchor-placement note as an Observation — it is not a fact about the code, it is the verifier flagging my own review-construction error, so I treated it as a directive to fix the anchor rather than as publishable content. See § 10 for that judgment call in full.
- **Coverage:** complete — every file in the 10-file changed manifest is `reviewed` or `ignored` (with a reason) by both finders; no fetch or check was abandoned.
- **Derived status:** `Changes Requested (advisory)` — 3 unsettled `must-fix` findings (step 1 of the `publishing.md` status ladder) forces this regardless of the other steps. Event `COMMENT` (per the packet's pinned posting-identity resolution and the retrospective-merged-target rule; publication disabled either way).
- **My own token usage:** the harness does not report token usage to me in this context; I have no such figure to give. (Per project memory, transcript-based token accounting exists as a separate tool the orchestrator runs after the fact; it is not available to me mid-run.) Each sub-agent's own usage, as reported by the harness at the end of its transcript: Code finder first dispatch — 97,487 tokens, 35 tool uses, 323s; Code finder shape-fix redispatch — 23,390 tokens, 0 tool uses, 37s; Requirements finder first dispatch — 196,577 tokens, 74 tool uses, 892s; Requirements finder shape-fix redispatch — 31,353 tokens, 3 tool uses, 61s; Verifier — 65,427 tokens, 35 tool uses, 305s.

This report is written in stages as the dispatch instructs: this metadata/manifest section and the requirement ledger are written before any finder is dispatched; the complete candidate ledger is appended once both finders return and are validated; the verifier prompt and its verbatim report are appended once it returns.

## 2. Findings for publication

Full rendered text (tag line, evidence, trigger, change, trailer) for every finding is in the payload at `/tmp/holdout/reports/c/panel-seed1-payload.md`; this section gives the same 8 findings in ledger form with their verification status and evidence, plus the anchor corrections I made at publish time (§ 10 explains why).

| # | id | priority/action | anchor (as published) | verifier verdict + decisive evidence | trigger scenario |
|---|---|---|---|---|---|
| 1 | `requirements/redis-init-reexports` | P1 must-fix | `stubs/redis/redis/credentials.pyi:3` | confirmed — quoted upstream `redis/__init__.py:67` `"CredentialProvider",` vs. no matching entry anywhere in `stubs/redis/redis/__init__.pyi` | `from redis import CredentialProvider` / `from redis import default_backoff` rejected by a type checker |
| 2 | `requirements/redis-retry-accessors` | P1 must-fix | none (body only — spans 5 files, no diff line opens or demonstrates the gap) | confirmed — quoted upstream `redis/cluster.py:382` `def replace_default_node(...)` vs. no match in `stubs/redis/redis/cluster.pyi`; I independently confirmed `get_retry`/`set_retry` at `redis/cluster.py:701,704` too | `redis_client.get_retry()`, `pool.set_retry(r)`, or `cluster.replace_default_node(node)` rejected |
| 3 | `requirements/asyncio-can-read-destructive` (merged with Code's `code/asyncio-connection-pyi/missing-can-read-destructive`) | P1 must-fix (**raised from P2/consider by the verifier**) | `stubs/redis/redis/asyncio/connection.pyi:135` (corrected from the Requirements finder's original `:48` — see § 10) | confirmed — quoted upstream `redis/asyncio/connection.py:776` `async def can_read_destructive(self):` vs. absent by name anywhere in the stub | `await connection.can_read_destructive()` (called by `redis-py`'s own `ConnectionPool.get_connection`) rejected |
| 4 | `requirements/backoff-default-backoff` | P2 consider | `stubs/redis/redis/backoff.pyi:16` | confirmed — quoted upstream `redis/backoff.py:113` `def default_backoff():` vs. absent from `stubs/redis/redis/backoff.pyi` | `from redis.backoff import default_backoff` / `redis.backoff.DEFAULT_CAP` rejected |
| 5 | `requirements/bitfield-ro` | P2 consider | none (body only — the file's touched lines are all topically unrelated to `bitfield_ro`) | confirmed — quoted upstream `redis/commands/core.py:1507` `def bitfield_ro(` vs. absent from the stub | `redis_client.bitfield_ro(key, "u8", "#0")` rejected |
| 6 | `requirements/max-connections-error` | P2 consider | none (body only — `exceptions.pyi` untouched by this PR) | confirmed — quoted upstream `redis/exceptions.py:204` `class MaxConnectionsError(ConnectionError):` (the only hunk in that file's diff) vs. absent from `stubs/redis/redis/exceptions.pyi`'s 20 exception classes | `except redis.exceptions.MaxConnectionsError:` rejected |
| 7 | `requirements/expiry-t-narrowing` | P2 consider | none (body only — `typing.pyi` untouched by this PR) | confirmed — quoted `stubs/redis/redis/typing.pyi:14` `ExpiryT: TypeAlias = float \| timedelta` vs. upstream `redis/typing.py:19` `ExpiryT = Union[int, timedelta]` | `redis_client.expire(key, 1.5)` (a float) accepted by the stub where upstream's own 4.4.0 annotation would flag it |
| 8 | `requirements/get-message-timeout-none` | P3 consider | none (body only — `get_message` untouched by this PR) | confirmed — quoted `stubs/redis/redis/asyncio/client.pyi:161` `timeout: float = ...` vs. upstream `redis/asyncio/client.py:896` `timeout: Optional[float] = 0.0` | `await pubsub.get_message(timeout=None)` rejected |

Plus 1 question (`requirements/submodule-interface-parity-undecidable`, no priority/action — questions carry neither) and 3 observations (see payload). 0 refuted (none occurred — the verifier confirmed all 9 candidates it received; see § 1 for the correction of my earlier, pre-verifier expectation of a `plausible`/second question).

## 3. Complete private disposition ledger

One row per candidate/hypothesis raised by either finder, verbatim from their `ledger` fenced blocks (post shape-fix), with the verifier's verdict added as a final column where the row's disposition was `candidate` (the verifier does not touch `acquitted`/`observation`/`question` rows — those are the finder's own private falsification record and the question channel respectively).

### Code axis ledger (14 rows)

| claim | falsification route | decisive evidence | disposition | verifier verdict |
|---|---|---|---|---|
| asyncio Connection/BaseParser/PythonParser/HiredisParser lost `can_read` with no `can_read_destructive` replacement | grep `can_read` in head stub vs. upstream 4.4.0 definitions | `stubs/redis/redis/asyncio/connection.pyi:135` | candidate | confirmed (merged into `requirements/asyncio-can-read-destructive`) |
| `xautoclaim` `start_id`: `StreamIdT` swap matches upstream `typing.py` alias | compared stub alias to upstream `typing.py` | `redis-py-4.4.0/redis/typing.py:30` | acquitted | — |
| `credentials.pyi` `CredentialProvider.get_credentials` return type matches upstream | compared stub return type to upstream implementation | `redis-py-4.4.0/redis/credentials.py:10` | acquitted | — |
| `UsernamePasswordCredentialProvider.username`/`password` typed `str`, not `str`-or-`None`, despite Optional ctor args | ctor coerces `None` via `or ""` at runtime so attrs are always `str` | `redis-py-4.4.0/redis/credentials.py:21` | acquitted | — |
| `credentials.pyi` marks `get_credentials` `@abstractmethod` though `CredentialProvider` is not an ABC subclass | checked stub and upstream class bases | `stubs/redis/redis/credentials.pyi:3` | observation | — (pooled into published Observations, deduplicated against Requirements' matching row) |
| `backoff.pyi` `cap`/`base` becoming defaulted matches upstream `DEFAULT_CAP`/`DEFAULT_BASE` | compared stub defaults to upstream constants | `redis-py-4.4.0/redis/backoff.py:48` | acquitted | — |
| `cluster.pyi` `retry` param addition matches upstream `RedisCluster.__init__` | compared stub param to upstream signature | `redis-py-4.4.0/redis/cluster.py:458` | acquitted | — |
| `cluster.pyi` `__nonzero__` removal matches upstream Python-2 method deletion in 4.4.0 | diffed 4.3.5 vs 4.4.0 `cluster.py` | `redis-py-4.3.5/redis/cluster.py:1801` | acquitted | — |
| asyncio `sentinel.pyi` `read_response` `type: ignore[override]` is warranted since `Connection` gained a `timeout` param this diff | compared `SentinelManagedConnection` arity to `Connection.read_response` | `stubs/redis/redis/asyncio/connection.pyi:135` | acquitted | — (verifier independently surfaced a sharper version of this as its own Observation — see § 2's observations pool) |
| asyncio `client.pyi` `lock()` `blocking` param position matches upstream `Redis.lock` | compared stub param order to upstream signature | `redis-py-4.4.0/redis/asyncio/client.py:357` | acquitted | — |
| `credential_provider` param order/position across `client.pyi`, `connection.pyi`, and asyncio variants matches upstream | compared all four `__init__` signatures to upstream | `redis-py-4.4.0/redis/client.py:944` | acquitted | — |
| `SocketBuffer` class removal from `asyncio/connection.pyi` matches upstream class deletion in 4.4.0 | diffed 4.3.5 vs 4.4.0 `asyncio/connection.py` | `redis-py-4.3.5/redis/asyncio/connection.py:210` | acquitted | — |
| sync `connection.pyi` `can_read`/`SocketBuffer` correctly left untouched since sync API is unrenamed upstream | grepped `can_read`/`SocketBuffer` in sync `connection.py` 4.4.0 | `redis-py-4.4.0/redis/connection.py:165` | acquitted | — |
| repo-wide sweep found no other stale prose/doc reference to `can_read` or `SocketBuffer` outside `stubs/redis` | repo-wide case-insensitive grep | `stubs/redis/redis/asyncio/connection.pyi:135` | acquitted | — |

### Requirements axis ledger (18 rows)

| claim | falsification route | decisive evidence | disposition | verifier verdict |
|---|---|---|---|---|
| `redis/__init__.pyi` and `asyncio/__init__.pyi` miss new `__all__` entries `CredentialProvider`/`UsernamePasswordCredentialProvider`/`default_backoff` | grep whole stub tree for the 3 new names | `stubs/redis/redis/credentials.pyi:3` | candidate | confirmed |
| `Redis`/`ConnectionPool`/`RedisCluster` miss new `get_retry`/`set_retry`/`replace_default_node` | grep whole stub tree for the 3 new names | `stubs/redis/redis/client.pyi:271` | candidate | confirmed |
| asyncio `connection.pyi` never gained `can_read_destructive` after `can_read` was removed | grep whole stub tree for `can_read_destructive` | `stubs/redis/redis/asyncio/connection.pyi:48` | candidate | confirmed (merged with Code's matching candidate; kept as `requirements/asyncio-can-read-destructive`, priority/action raised to P1/must-fix; anchor corrected to `:135` at publish time, see § 10) |
| `backoff.pyi` misses new `DEFAULT_CAP`/`DEFAULT_BASE`/`default_backoff` | grep whole stub tree for `default_backoff` | `stubs/redis/redis/backoff.pyi:16` | candidate | confirmed |
| `commands/core.pyi` misses new `bitfield_ro` command | grep whole stub tree for `bitfield_ro` | `stubs/redis/redis/commands/core.pyi:10` | candidate | confirmed |
| `exceptions.pyi` misses new `MaxConnectionsError` | grep whole stub tree for `MaxConnectionsError` | `stubs/redis/METADATA.toml:2` | candidate | confirmed |
| `typing.pyi`'s `ExpiryT` not narrowed from `float` to `int` | diff `redis/typing.py` 4.3.5 vs 4.4.0 | `stubs/redis/redis/typing.pyi:14` | candidate | confirmed |
| async `PubSub.get_message` `timeout` not widened to `float`-or-`None` | diff `redis/asyncio/client.py` 4.3.5 vs 4.4.0 `get_message` | `stubs/redis/redis/asyncio/client.pyi:161` | candidate | confirmed |
| `bf`/`graph`/`json`/`redismodules`/`search`/`timeseries` submodule parity with 4.4.0 is undecidable | `diff -rq` the two provided tree snapshots for these 6 files | `redis-py-4.4.0/redis/commands/graph/__init__.py:12` | question | — (questions never reach the verifier) |
| `get_node_name`'s `port` param already `str`-or-`int`, matching upstream's widened type | diff `redis/cluster.py` 4.3.5 vs 4.4.0 `get_node_name` | `stubs/redis/redis/cluster.pyi:16` | acquitted | — |
| `smembers`'s return type already `set[_StrType]`, matching upstream's `Set` | diff `redis/commands/core.py` 4.3.5 vs 4.4.0 `smembers` | `stubs/redis/redis/commands/core.pyi:769` | acquitted | — |
| `lmpop` missing from stub is pre-existing since 4.3.5, unrelated to this version-bump delta | diff `lmpop` def between 4.3.5 and 4.4.0 sources | `redis-py-4.3.5/redis/commands/core.py:2534` | acquitted | — |
| `TDigestCommands` `trimmed_mean`/`rank`/`revrank`/`byrank`/`byrevrank` already present at 4.3.5, unchanged going into 4.4.0 | diff of `TDigestCommands` method list 4.3.5 vs 4.4.0 | `redis-py-4.3.5/redis/commands/bf/commands.py:356` | acquitted | — (this row is the one I independently re-verified and that surfaced the `.diff`-file-vs-tree-snapshot contradiction — see § 4.2 and § 10) |
| `utils.py` `warn_deprecated`/`deprecated_function` already existed at 4.3.5, unchanged into 4.4.0 | diff `redis/utils.py` 4.3.5 vs 4.4.0 | `redis-py-4.3.5/redis/utils.py:85` | acquitted | — |
| `EXCEPTION_CLASSES` new error-string keys (`WRONGPASS`, `NO_AUTH_SET_ERROR`) need no stub change, attribute is typed generically | checked stub type annotation | `stubs/redis/redis/connection.pyi:32` | acquitted | — |
| `SentinelManagedConnection.read_response` `type: ignore[override]` correctly matches upstream's un-widened override signature | compared `SentinelManagedConnection.read_response` to base `Connection.read_response` | `redis-py-4.4.0/redis/asyncio/sentinel.py:66` | acquitted | — |
| asyncio `Lock.redis` narrowed to `Redis[Any]` though upstream 4.4.0 widens to `Union[Redis, RedisCluster]`; fix blocked by `asyncio.cluster` being wholly unstubbed | diff `redis/asyncio/lock.py` 4.3.5 vs 4.4.0 `__init__` | `stubs/redis/redis/asyncio/lock.pyi:26` | observation | — (published, independently re-verified — see § 10) |
| `credentials.pyi` marks `CredentialProvider.get_credentials` `@abstractmethod` though the stubbed class has no ABC base | read `stubs/redis/redis/credentials.pyi` | `stubs/redis/redis/credentials.pyi:4` | observation | — (deduplicated with Code's matching row, published once) |

### Verifier's own additions (not candidates, do not enter the ledger above)

| item | disposition | published? |
|---|---|---|
| `sentinel.pyi:18` — `type: ignore[override]` silences rather than resolves the Liskov mismatch this diff introduced | observation | yes — published (3rd observation) |
| `METADATA.toml:2` anchor doesn't exist (file is 1 line); candidates 6 and 7's anchors were invalid | observation (verifier's own label) | **no** — I treated this as a correction to make, not a fact about the code to publish; see § 10 |

## 4. Every sub-agent dispatch

Three sub-agents total, all `Agent` calls with `model: "sonnet"` explicitly passed, all `run_in_background: false` (foreground), all dispatched one after another with each fully awaited before the next was sent. Each finder's shared-block prefix is byte-identical (verified with `diff` on the first 988 lines of both prompt files — see § 6 above); the axis-specific block differs, as the skill requires.

### 4.1 Code finder (first dispatch — shape violation, re-dispatched once)

**Model:** `claude-sonnet-5` (`model: "sonnet"` on the `Agent` call).

**Prompt (verbatim, as given to the sub-agent):**

> Read the file at /tmp/holdout/work/c/panel-seed1/prompt-code-finder.md in full, from top to bottom. That file is your entire prompt — a shared input block followed by your axis-specific block. It tells you which brief to read first (an absolute path to code-axis.md), what materials you have (a git clone, an upstream reference tree, a full diff, guidance files), and the exact constraints you must operate under (offline, no execution, clone hygiene, sandbox limits, no session relays). Follow it exactly and completely, in the order it specifies: read the axis brief first, then do the Code-axis review it describes against the diff and repository in that file.
>
> Do not read any file outside what that prompt file and the brief it points you to authorize (the clone at /tmp/holdout/runs/c/panel-seed1, the skill snapshot at /tmp/holdout/skills/panel/, and the packet directory at /tmp/holdout/packets/c/ including its upstream/ subtree). Do not run git checkout, git switch, git reset, git stash, or anything else that mutates the working tree. Do not run python, mypy, pyright, stubtest, pre-commit, flake8, or any test/lint/build command. Do not use any network tool (no fetch, no gh, no curl-equivalent).
>
> Return your complete finder report as your final message, formatted exactly as the code-axis.md brief specifies, ending with the two required fenced blocks (`ledger` then `manifest`) and nothing after them. Do not stop to ask anything — if something is genuinely missing, apply the brief's own incomplete-coverage handling and say so in your report. This is a one-shot dispatch: finish entirely in this turn.

The prompt file it was told to read (`/tmp/holdout/work/c/panel-seed1/prompt-code-finder.md`) is the concatenation of the shared block (`shared-block.md`, built by `scripts/build_shared_block.py`) and the Code axis-specific block (`code-axis-block.md`, authored by me per SKILL.md § 2's instructions for what that block must contain) — both files are preserved on disk at those paths, unmodified since dispatch.

**Verbatim report (first attempt, before shape-fix):** reproduced in full at `/tmp/holdout/work/c/panel-seed1/finder-code.md`'s git history is not tracked, but the content is identical to what is quoted below except for two ledger rows — see § 4.1a.

**Shape validation:** `python3 scripts/validate_finder_report.py --axis code --manifest manifest.tsv` on the first-attempt report returned exit 1 with two violations: row 4 of the ledger had a stray `|` inside a claim ("str not str | None"), producing five fields instead of four; row 14's evidence field ("stubs/redis/ (no hits elsewhere)") was prose, not a `path:line`/`path:start-end`/quoted-rule coordinate.

**Re-dispatch (§ 4.1a):** per SKILL.md § 2 ("re-dispatch that finder once with its original prompt plus the violation lines and the instruction to return the same review in conforming shape; do not re-run the investigation"), I dispatched a second `Agent` call (`model: "sonnet"`, foreground) carrying the finder's own prior report verbatim plus the two violation lines, instructing it to fix only those two rows' shape and change nothing else. It returned the same report with row 4 reworded ("str, not str-or-None") and row 14's evidence changed to `stubs/redis/redis/asyncio/connection.pyi:135` (the file the sweep was keyed from). Re-validated: exit 0, no violations.

**Final verbatim report** (this is what was carried forward into the verifier prompt and this run's ledger) — saved at `/tmp/holdout/work/c/panel-seed1/finder-code.md`, reproduced here in full:

```markdown
## Report — Code axis, redis stub review (panel-seed1)

**History/constraint disclosure:** I ran only read-only git commands against `/tmp/holdout/runs/c/panel-seed1`: `git branch -a`, `git log --oneline -3 main`, `git log --oneline -3 review-head`. Both logs show only the already-pinned base tip (`8365b1aae...`) and head tip (`55dfb4511...`); I did not read, and did not attempt to read, any commit history beyond the pinned head. No `git checkout`/`switch`/`reset`/`stash` was run — the working tree was left as found (on `review-head`), and I read file contents only via `cat`/`sed`/`grep`, never editing anything. All reads stayed within the authorized paths: the clone at `/tmp/holdout/runs/c/panel-seed1`, the skill snapshot at `/tmp/holdout/skills/panel/references/{code-axis.md,finding-format.md}`, and the packet directory `/tmp/holdout/packets/c/upstream/` (both `redis-py-4.3.5/` and `redis-py-4.4.0/` trees). No network tool, no execution of python/mypy/pyright/stubtest/pre-commit/flake8/tests was used.

### Method

I read every hunk in the diff, read the enclosing class in the current stub tree for each, and cross-checked every non-trivial signature change against the actual upstream `redis-py` source at both the 4.3.5 and 4.4.0 tags to tell a faithful version-bump change from a genuine stub defect. I also ran a sync-drift sweep (`grep -rni` for the retired vocabulary `can_read`, `SocketBuffer`, and the old `int`-typed `start_id`) across the whole repository tree, not just `stubs/redis/`.

### Candidate found

**id:** `code/asyncio-connection-pyi/missing-can-read-destructive` — anchor `stubs/redis/redis/asyncio/connection.pyi:135`, fix scattered across the four class sites — the diff removes `can_read` from `BaseParser`/`PythonParser`/`HiredisParser`/`Connection` in `stubs/redis/redis/asyncio/connection.pyi` but never adds `can_read_destructive`, the method upstream renamed it to (confirmed against both upstream tags; `ConnectionPool.get_connection` calls it as normal operation). P1, must-fix.

(Full field-by-field text is identical to the `candidates` block below; see there for the complete claim/support/trigger.)

````candidates
### Candidate
id: code/asyncio-connection-pyi/missing-can-read-destructive
axis: Code
anchor: stubs/redis/redis/asyncio/connection.pyi:135
fix: stubs/redis/redis/asyncio/connection.pyi
title: asyncio connection.pyi drops can_read without adding can_read_destructive
claim: The diff removes `can_read` from `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `stubs/redis/redis/asyncio/connection.pyi` (old lines 49, 71, 78, 152) but never declares `can_read_destructive`, the method upstream renamed it to. Upstream redis-py 4.4.0 `redis/asyncio/connection.py` defines `async def can_read_destructive(self) -> bool:` on `BaseParser` (line 199), `PythonParser` (line 231), `HiredisParser` (line 344), and `Connection` (line 776), and `ConnectionPool.get_connection` (lines 1369, 1376) calls `await connection.can_read_destructive()` as normal operation. After this diff, `grep -n can_read stubs/redis/redis/asyncio/connection.pyi` returns no matches anywhere in the stub.
support: Static diff-only review. Confirmed the rename by comparing redis-py-4.3.5 (has `can_read`, `SocketBuffer`) against redis-py-4.4.0 (has `can_read_destructive` on all four classes, `SocketBuffer` deleted) in the provided upstream packet. Confirmed `SocketBuffer`'s removal is correct (class deleted upstream too) so only the `can_read` rename was mishandled. Confirmed sync `redis/connection.pyi` was correctly left untouched (sync API didn't rename `can_read`). Repo-wide grep found no other stale `can_read` reference.
trigger: Any type-checked call to `await connection.can_read_destructive()` on `redis.asyncio.connection.Connection` (including inside redis-py's own `ConnectionPool.get_connection`) or to a parser's `can_read_destructive()` is flagged as an unknown attribute even though it is valid, documented runtime behavior.
priority: P1
action: must-fix
````

```ledger
asyncio Connection/BaseParser/PythonParser/HiredisParser lost can_read with no can_read_destructive replacement | grep can_read in head stub vs upstream 4.4.0 definitions | stubs/redis/redis/asyncio/connection.pyi:135 | candidate
xautoclaim start_id: StreamIdT swap matches upstream typing.py alias | compared stub alias to upstream typing.py | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/typing.py:30 | acquitted
credentials.pyi CredentialProvider.get_credentials return type matches upstream | compared stub return type to upstream implementation | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/credentials.py:10 | acquitted
UsernamePasswordCredentialProvider.username/password typed str, not str-or-None, despite Optional ctor args | ctor coerces None via `or ""` at runtime so attrs are always str | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/credentials.py:21 | acquitted
credentials.pyi marks get_credentials @abstractmethod though CredentialProvider is not an ABC subclass | checked stub and upstream class bases | stubs/redis/redis/credentials.pyi:3 | observation
backoff.pyi cap/base becoming defaulted matches upstream DEFAULT_CAP/DEFAULT_BASE | compared stub defaults to upstream constants | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/backoff.py:48 | acquitted
cluster.pyi retry param addition matches upstream RedisCluster.__init__ | compared stub param to upstream signature | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/cluster.py:458 | acquitted
cluster.pyi __nonzero__ removal matches upstream Python-2 method deletion in 4.4.0 | diffed 4.3.5 vs 4.4.0 cluster.py | /tmp/holdout/packets/c/upstream/redis-py-4.3.5/redis/cluster.py:1801 | acquitted
asyncio sentinel.pyi read_response type: ignore[override] is warranted since Connection gained a timeout param this diff | compared SentinelManagedConnection arity to Connection.read_response | stubs/redis/redis/asyncio/connection.pyi:135 | acquitted
asyncio client.pyi lock() blocking param position matches upstream Redis.lock | compared stub param order to upstream signature | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/asyncio/client.py:357 | acquitted
credential_provider param order/position across client.pyi, connection.pyi, and asyncio variants matches upstream | compared all four __init__ signatures to upstream | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/client.py:944 | acquitted
SocketBuffer class removal from asyncio/connection.pyi matches upstream class deletion in 4.4.0 | diffed 4.3.5 vs 4.4.0 asyncio/connection.py | /tmp/holdout/packets/c/upstream/redis-py-4.3.5/redis/asyncio/connection.py:210 | acquitted
sync connection.pyi can_read/SocketBuffer correctly left untouched since sync API is unrenamed upstream | grepped can_read/SocketBuffer in sync connection.py 4.4.0 | /tmp/holdout/packets/c/upstream/redis-py-4.4.0/redis/connection.py:165 | acquitted
repo-wide sweep found no other stale prose/doc reference to can_read or SocketBuffer outside stubs/redis | repo-wide case-insensitive grep | stubs/redis/redis/asyncio/connection.pyi:135 | acquitted
```
```manifest
stubs/redis/METADATA.toml | reviewed | trivial version bump 4.3.5 -> 4.4.0 matching the pinned upstream tags; nothing to flag
stubs/redis/redis/asyncio/client.pyi | reviewed | credential_provider, StreamIdT, and lock() blocking-param additions all verified against upstream redis-py 4.4.0 asyncio/client.py; no defects
stubs/redis/redis/asyncio/connection.pyi | reviewed | candidate found: can_read removed without adding its upstream replacement can_read_destructive
stubs/redis/redis/asyncio/sentinel.pyi | reviewed | added type: ignore[override] comment verified correct given Connection.read_response gained a timeout param this diff
stubs/redis/redis/backoff.pyi | reviewed | cap/base becoming defaulted verified against upstream 4.4.0 DEFAULT_CAP/DEFAULT_BASE
stubs/redis/redis/client.pyi | reviewed | credential_provider addition to three __init__ overloads verified against upstream redis/client.py
stubs/redis/redis/cluster.pyi | reviewed | retry param addition and __nonzero__ removal both verified against upstream redis/cluster.py 4.4.0
stubs/redis/redis/commands/core.pyi | reviewed | StreamIdT swap for xautoclaim start_id (sync and async) verified against upstream redis/typing.py
stubs/redis/redis/connection.pyi | reviewed | credential_provider addition to Connection/UnixDomainSocketConnection verified against upstream redis/connection.py 4.4.0
stubs/redis/redis/credentials.pyi | reviewed | new file; types verified against upstream redis/credentials.py 4.4.0; abstractmethod-on-non-ABC noted only as an observation
```
```

### 4.2 Requirements finder (first dispatch — shape violation, re-dispatched once)

**Model:** `claude-sonnet-5` (`model: "sonnet"` on the `Agent` call).

**Prompt (verbatim, as given to the sub-agent):**

> Read the file at /tmp/holdout/work/c/panel-seed1/prompt-requirements-finder.md in full, from top to bottom. That file is your entire prompt — a shared input block followed by your axis-specific block. It tells you which brief to read first (an absolute path to requirements-axis.md), the originating issue text (a closed pull request whose body/comments are the spec source), any explicit deferrals from prior review, and the exact constraints you must operate under (offline, no execution, clone hygiene, sandbox limits, no session relays). Follow it exactly and completely, in the order it specifies: read the axis brief first, then do the Requirements-axis review it describes — restate requirements, sort them, sweep for changed-contract peers, look for unrequested scope creep.
>
> Do not read any file outside what that prompt file and the brief it points you to authorize (the clone at /tmp/holdout/runs/c/panel-seed1, the skill snapshot at /tmp/holdout/skills/panel/, and the packet directory at /tmp/holdout/packets/c/ including its upstream/ subtree). Do not run git checkout, git switch, git reset, git stash, or anything else that mutates the working tree. Do not run python, mypy, pyright, stubtest, pre-commit, flake8, or any test/lint/build command. Do not use any network tool (no fetch, no gh, no curl-equivalent).
>
> Return your complete finder report as your final message, formatted exactly as the requirements-axis.md brief specifies, ending with the three required fenced blocks (`ledger`, `manifest`, `counts`, in that order) and nothing after them. Do not stop to ask anything — if something is genuinely missing, apply the brief's own incomplete-coverage handling and say so in your report. This is a one-shot dispatch: finish entirely in this turn.

The prompt file (`/tmp/holdout/work/c/panel-seed1/prompt-requirements-finder.md`) is the concatenation of the same `shared-block.md` (byte-identical to the Code finder's copy) and `requirements-axis-block.md`, which I authored to include: the axis brief pointer, the originating issue text (`python/typeshed#9329`) verbatim, the upstream reference-tree pointers, and the explicit-deferrals paragraph (I found none, having reread the full prior-review record reproduced in the packet — see § 10 Notes for that judgment call).

**Shape validation:** first attempt failed with 4 violations (two stray `|` characters inside claims — "float | None", "str | int" — and two bare-path evidence fields with no line number, rows 9 and 13). Re-dispatched once, per the same re-dispatch rule, with the finder's own prior report plus the violation lines; it fixed exactly those four rows (rewording the two claims, and reading the two named upstream files to cite real line numbers: `redis/commands/graph/__init__.py:12` and `redis/commands/bf/commands.py:356`) and changed nothing else. Re-validated: exit 0.

**Independent spot-check I performed on this finder's most consequential claim** (the "cannot tell" question about `bf`/`graph`/`redismodules`/`search`/`timeseries` submodule parity, where it reported that the packet's `.diff` file and its two tree snapshots disagree): I ran `diff -q` myself between the two tree snapshots on all seven files the `.diff` file shows hunks for, and separately grepped the `.diff` file's `diff --git` headers for the same paths. Confirmed independently: all seven files are byte-identical between `redis-py-4.3.5/` and `redis-py-4.4.0/` in the tree snapshots, yet the `.diff` file contains real hunks for all seven (e.g. `TDIGEST_TRIMMED_MEAN`, `deprecated_function` additions to `bf/commands.py`). I further confirmed that `redis-py-4.3.5/redis/commands/bf/commands.py` (the tree snapshot, not the diff) *already* contains `TDIGEST_TRIMMED_MEAN` and `deprecated_function`, i.e. the "4.3.5" tree snapshot is not self-consistent with the `.diff` file's claim that these were introduced only in the 4.3.5→4.4.0 transition. This is a genuine, packet-level evidence contradiction, not a finder hallucination — it independently validates the finder's decision to route this to a question rather than assert a defect either way.

**Final verbatim report** (this is what was carried forward into the verifier prompt and this run's ledger) — saved at `/tmp/holdout/work/c/panel-seed1/finder-requirements.md`; reproduced below in full:



````markdown
# Requirements-axis finder report — stubs/redis 4.3.5 → 4.4.0 (typeshed, closes python/typeshed#9329)

## Process note (binding constraints, addressed up front)

Read `/tmp/holdout/skills/panel/references/finding-format.md` and `/tmp/holdout/skills/panel/references/requirements-axis.md` in full before starting, as directed. All work was static: no `python`/`mypy`/`pyright`/`stubtest`/`pre-commit`/`flake8`, no network. I ran only read-only git-adjacent inspection is not even needed — I did not run any `git log`/`git show`/`git blame`/`git diff` history commands at all against `/tmp/holdout/runs/c/panel-seed1`; the only commands run there were non-mutating `ls`/`find`/`git status`/`git log --oneline -5` (already-visible HEAD, no deeper history) to confirm the clone matched the pinned SHAs, and file reads under `stubs/redis/`. I did not read anything outside the clone at `/tmp/holdout/runs/c/panel-seed1`, the skill snapshot at `/tmp/holdout/skills/panel/`, and the packet directory at `/tmp/holdout/packets/c/` (including `upstream/`).

**Important evidence-source discrepancy, discovered mid-review:** the provided `.diff` file (`/tmp/holdout/packets/c/upstream/redis-py-4.3.5...4.4.0.diff`) claims substantive changes to `redis/commands/bf/commands.py`, `redis/commands/graph/__init__.py`, `redis/commands/graph/commands.py`, `redis/commands/graph/query_result.py`, `redis/commands/redismodules.py`, `redis/commands/search/__init__.py`, and `redis/commands/timeseries/commands.py`. A direct byte comparison of the two provided tree snapshots (`redis-py-4.3.5/` vs `redis-py-4.4.0/`) shows every one of those files is **identical** between the two tags — `diff -rq` reports no difference for any of them. Since my two authorized offline sources disagree and I have no network access to resolve which is right, I cannot determine whether those six submodules' public interfaces actually changed at all between 4.3.5 and 4.4.0. I therefore could not safely check the stub's silence on those modules — see the `question` candidate below. All other findings in this report are grounded in direct tree-to-tree diffs (`diff -u redis-py-4.3.5/... redis-py-4.4.0/...`), not the `.diff` file, specifically because the `.diff` file proved unreliable for at least this subset of paths.

## Step 1: restated requirements

The issue (`python/typeshed#9329`, a stubsabot auto-PR, `Closes #9329`) carries no line-item spec — its substance is: **bring the typeshed `redis` stubs' public interface back into alignment with what changed in `redis-py` between v4.3.5 and v4.4.0.** I decomposed that into the concrete interface deltas I could verify by direct tree comparison of the two upstream snapshots:

1. Bump `METADATA.toml` version to `4.4.0`.
2. Add `credential_provider: CredentialProvider | None` to `Redis.__init__` (sync + async) and to `Connection`/`UnixDomainSocketConnection.__init__` (sync + async), matching new `redis/credentials.py`.
3. Add a `redis/credentials.pyi` stub for the new `CredentialProvider`/`UsernamePasswordCredentialProvider` classes.
4. Re-export `CredentialProvider`, `UsernamePasswordCredentialProvider`, and `default_backoff` from `redis/__init__.pyi`'s (and `default_backoff` from `redis/asyncio/__init__.pyi`'s) `__all__`/namespace, matching upstream's expanded `__all__`.
5. Add `blocking: bool` to async `Redis.lock()`.
6. Add `Redis.get_retry()`/`set_retry()` (sync+async), `ConnectionPool.set_retry()` (sync+async), and `RedisCluster.get_retry()`/`set_retry()`/`replace_default_node()`.
7. Rename `can_read(timeout)` → `can_read_destructive()` (no timeout) on `BaseParser`/`PythonParser`/`HiredisParser`/`Connection` in the async connection module.
8. Fix `HiredisParser.read_from_socket`'s signature/return type (async).
9. Remove `SocketBuffer`, `NONBLOCKING_EXCEPTION_ERROR_NUMBERS`, `NONBLOCKING_EXCEPTIONS` (async, all deleted upstream).
10. Add `disconnect(nowait: bool)` and fold `read_response_without_lock` into `read_response(..., timeout: float | None)` (async `Connection`).
11. Give the four Backoff subclasses' `cap`/`base` defaults.
12. Add `DEFAULT_CAP`, `DEFAULT_BASE`, `default_backoff()` to `backoff.pyi` (and re-export, folded into #4).
13. Fix `xautoclaim`'s `start_id` from `int` to `StreamIdT` (sync+async mixins, async `Pipeline`).
14. Add the new `bitfield_ro` command method.
15. Remove `ClusterPipeline.__nonzero__` (py2 alias, deleted upstream).
16. Add `retry: Retry | None` to `RedisCluster.__init__`.
17. Add the new `MaxConnectionsError` exception.
18. Narrow `ExpiryT` from `float | timedelta` to `int | timedelta`.
19. Widen async `PubSub.get_message`'s `timeout` to `float | None`.
20. Resolve `SentinelManagedConnection.read_response`'s signature mismatch against the base class's new `timeout` param (async).
21. Reflect any interface changes in `redis.commands.{bf,graph,json,redismodules,search,timeseries}` between the two tags.

Background/non-requirements noted but not restated as requirements: the PR body is just `Closes #9329`; the linked PR's own comments are process (rebase policy, thanks) or bot noise (mypy_primer), not requirements. Per the run's pinned resolution, no comment in the review record explicitly defers a design/naming/API-shape decision — confirmed by re-reading the record as reproduced in the prompt; I found no additional candidate deferral.

## Step 2: sorting

**Met** (12): #1–#3, #5, #8–#11, #13, #15, #16, #20 — all verified directly against the diff-touched `.pyi` files and cross-checked against the corresponding upstream `.py` source via direct tree diff (not the unreliable `.diff` artifact).

**Not met** (8): #4, #6, #7, #12, #14, #17, #18, #19 — see candidates.

**Cannot tell from the code** (1): #21 — see the question candidate; the two authorized offline sources disagree, and resolving it needs network access I don't have (either re-fetching the true GitHub compare for those six files, or re-deriving a diff from the tree snapshots themselves — I did the latter for as much as I safely could, which is exactly what produced the "identical" finding above; I cannot determine which of the `.diff` file or the tree snapshots is the accurate one for these six files without a third, independent source).

## Changed-contract peer sweep

Three contracts changed between the tags in ways with typeshed-wide reach:

**Contract A — top-level `__all__` re-export lists** (`redis/__init__.py`, `redis/asyncio/__init__.py`). New terms added upstream: `CredentialProvider`, `UsernamePasswordCredentialProvider`, `default_backoff`. Search 1 (new terms) across `stubs/redis/`: `CredentialProvider` found in `client.pyi`, `credentials.pyi`, `connection.pyi`, `asyncio/connection.pyi`, `asyncio/client.pyi` — **absent** from `redis/__init__.pyi`. `default_backoff` found **nowhere** in the stub tree. Search 2 (old wording — the pre-existing `__all__` list content, e.g. `"SentinelManagedSSLConnection"`) locates exactly the two peer lists that exist in the repo (`redis/__init__.pyi`, `redis/asyncio/__init__.pyi`) — both are live and both are stale (missing the new entries). Sweep complete: 2 live peers, both non-compliant.

**Contract B — the new `get_retry`/`set_retry`/`replace_default_node` retry-accessor surface**, added in parallel across `redis/client.py` (`Redis`), `redis/asyncio/client.py` (`Redis`), `redis/connection.py` (`ConnectionPool`), `redis/asyncio/connection.py` (`ConnectionPool`), and `redis/cluster.py` (`RedisCluster`). Search for `get_retry`/`set_retry`/`replace_default_node` across `stubs/redis/`: **zero hits**. Sweep complete: 5 live peers (the 5 classes above), all missing the new methods.

**Contract C — `can_read` → `can_read_destructive` rename** (async parser/connection classes only; sync `connection.py` was not touched and still uses `can_read`, correctly unchanged in the sync stub). Search for `can_read_destructive`: zero hits anywhere in the stub tree. Search for the old fragment `can_read` in `stubs/redis/redis/asyncio/`: zero hits (the old name was fully and correctly removed by this PR) — so the gap is a pure omission of the new name, not a stale old name left behind. Sweep complete: the rename's target (`BaseParser`, `PythonParser`, `HiredisParser`, `Connection` in `redis/asyncio/connection.pyi`) never received the new method.

## Step 3: unrequested scope creep

None found. Every hunk in the diff maps to a verified upstream interface change (see Step 2 met list); I found no new user-visible behavior, public interface, dependency, or abstraction beyond what the version bump required.

---

## Candidates

### 1 — `requirements/redis-init-reexports`
**Claim:** Upstream `redis/__init__.py` 4.4.0 adds `from redis.credentials import CredentialProvider, UsernamePasswordCredentialProvider` and `from redis.backoff import default_backoff`, adding `"CredentialProvider"`, `"default_backoff"`, `"UsernamePasswordCredentialProvider"` to `__all__`; `redis/asyncio/__init__.py` adds `from redis.backoff import default_backoff` and `"default_backoff"` to its `__all__`. `stubs/redis/redis/__init__.pyi` and `stubs/redis/redis/asyncio/__init__.pyi` were not touched by this PR and still lack all of these — `redis/__init__.pyi`'s `__all__` (lines 4–31) has no `CredentialProvider`/`UsernamePasswordCredentialProvider`/`default_backoff` entry and no corresponding assignment; `asyncio/__init__.pyi`'s `__all__` (lines 32–58) has no `default_backoff`.
**Trigger:** `from redis import CredentialProvider` or `from redis import default_backoff` — both valid at runtime and both part of the feature this very PR wired through everywhere else — are rejected by a type checker.
**Change:** In `stubs/redis/redis/__init__.pyi`, import `CredentialProvider`/`UsernamePasswordCredentialProvider` from `.credentials` and `default_backoff` from `.backoff`, add all three to `__all__` and assign them (matching the file's existing re-export idiom). In `stubs/redis/redis/asyncio/__init__.pyi`, add `default_backoff` the same way (also requires fixing candidate 4 first, since `default_backoff` doesn't exist in `backoff.pyi` yet).
**Priority:** P1 **Action:** must-fix

### 2 — `requirements/redis-retry-accessors`
**Claim:** Upstream 4.4.0 adds `Redis.get_retry()`/`set_retry()` to both `redis/client.py` and `redis/asyncio/client.py`, `ConnectionPool.set_retry()` to both `redis/connection.py` and `redis/asyncio/connection.py`, and `RedisCluster.get_retry()`/`set_retry()`/`replace_default_node()` to `redis/cluster.py` (all confirmed absent in the 4.3.5 tree and present in 4.4.0 via direct `def`-level tree diff). None of these five locations in `stubs/redis/` gained the corresponding methods — `client.pyi`, `asyncio/client.pyi`, `connection.pyi`, `asyncio/connection.pyi`, `cluster.pyi` all lack `get_retry`/`set_retry`/`replace_default_node` entirely.
**Trigger:** `redis_client.get_retry()`, `pool.set_retry(new_retry)`, or `cluster.replace_default_node(node)` — all valid at runtime — is rejected by a type checker with "has no attribute".
**Change:** Add `def get_retry(self) -> Retry | None: ...` / `def set_retry(self, retry: Retry) -> None: ...` to `Redis` in `client.pyi` and `asyncio/client.pyi`; `def set_retry(self, retry: Retry) -> None: ...` to `ConnectionPool` in `connection.pyi` and `asyncio/connection.pyi`; and `get_retry`/`set_retry`/`def replace_default_node(self, target_node: ClusterNode | None = ...) -> None: ...` to `RedisCluster` in `cluster.pyi`.
**Priority:** P1 **Action:** must-fix

### 3 — `requirements/asyncio-can-read-destructive`
**Claim:** Upstream 4.4.0 renames `async def can_read(self, timeout: float) -> bool` to `async def can_read_destructive(self) -> bool` (no `timeout` param) on `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `redis/asyncio/connection.py` (confirmed via direct tree diff). This PR's diff correctly deletes all four `can_read` stub lines but never adds `can_read_destructive` anywhere in `stubs/redis/redis/asyncio/connection.pyi`.
**Trigger:** `await connection.can_read_destructive()` — the method `ConnectionPool.get_connection` actually calls at runtime — is rejected by a type checker; the class instead appears to have lost the capability entirely.
**Change:** Add `async def can_read_destructive(self) -> bool: ...` to `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `stubs/redis/redis/asyncio/connection.pyi`.
**Priority:** P2 **Action:** consider

### 4 — `requirements/backoff-default-backoff`
**Claim:** Upstream 4.4.0 adds module-level `DEFAULT_CAP = 0.512`, `DEFAULT_BASE = 0.008`, and `def default_backoff(): return EqualJitterBackoff()` to `redis/backoff.py` (confirmed absent in 4.3.5, present in 4.4.0). `stubs/redis/redis/backoff.pyi` reflects the new `cap`/`base` defaults on the four Backoff subclasses (met) but has no `DEFAULT_CAP`, `DEFAULT_BASE`, or `default_backoff` at all.
**Trigger:** `from redis.backoff import default_backoff` or `redis.backoff.DEFAULT_CAP` — valid at runtime — rejected by a type checker.
**Change:** Add `DEFAULT_CAP: float`, `DEFAULT_BASE: float`, and `def default_backoff() -> EqualJitterBackoff: ...` to `stubs/redis/redis/backoff.pyi`.
**Priority:** P2 **Action:** consider

### 5 — `requirements/bitfield-ro`
**Claim:** Upstream 4.4.0 adds `def bitfield_ro(self, key, encoding, offset, items=None) -> ResponseT` to the shared `BasicKeyCommands` mixin in `redis/commands/core.py` (confirmed absent in 4.3.5). `stubs/redis/redis/commands/core.pyi` was touched by this PR (StreamIdT fix) but `bitfield_ro` is absent from both the sync and async mixin classes.
**Trigger:** `redis_client.bitfield_ro(key, "u8", "#0")` — a valid new 4.4.0 command — is rejected by a type checker.
**Change:** Add `def bitfield_ro(self, key: KeyT, encoding: str, offset: BitfieldOffsetT, items: list[Any] | None = ...) -> ResponseT: ...` (and the `Awaitable`-returning async variant) to `stubs/redis/redis/commands/core.pyi`.
**Priority:** P2 **Action:** consider

### 6 — `requirements/max-connections-error`
**Claim:** Upstream 4.4.0 adds `class MaxConnectionsError(ConnectionError): ...` to `redis/exceptions.py` (confirmed absent in 4.3.5, present in 4.4.0, and it is the *only* change to that file). `stubs/redis/redis/exceptions.pyi` was not touched by this PR and has no `MaxConnectionsError` class.
**Trigger:** `except redis.exceptions.MaxConnectionsError:` — valid, upstream-raised on pool exhaustion — is rejected by a type checker ("has no attribute").
**Change:** Add `class MaxConnectionsError(ConnectionError): ...` to `stubs/redis/redis/exceptions.pyi`.
**Priority:** P2 **Action:** consider
*(No diff-touched file in this PR relates topically to exceptions; per the anchor ladder I attach this to the version-bump line as the closest honest stand-in for "the change as a whole.")*

### 7 — `requirements/expiry-t-narrowing`
**Claim:** Upstream 4.4.0 narrows `ExpiryT = Union[float, timedelta]` to `ExpiryT = Union[int, timedelta]` in `redis/typing.py` (confirmed via direct diff; this is the only change to that file). `stubs/redis/redis/typing.pyi` was not touched by this PR and still declares `ExpiryT: TypeAlias = float | timedelta`. Since `ExpiryT` is used by reference throughout `commands/core.pyi` (`expire`, `setex`, `getex`, etc.), this one stale alias silently under-restricts every caller of those methods.
**Trigger:** `redis_client.expire(key, 1.5)` — a `float` the stub still accepts via `ExpiryT` — no longer matches what upstream's own 4.4.0 type annotations say the command accepts, so a type checker gives no warning where upstream's own typing intends one.
**Change:** Update `stubs/redis/redis/typing.pyi:14` to `ExpiryT: TypeAlias = int | timedelta`.
**Priority:** P2 **Action:** consider
*(No diff-touched file relates to `typing.pyi`; anchored to the version-bump line for the same reason as candidate 6.)*

### 8 — `requirements/get-message-timeout-none`
**Claim:** Upstream 4.4.0 changes async `PubSub.get_message`'s signature from `timeout: float = 0.0` to `timeout: Optional[float] = 0.0` in `redis/asyncio/client.py` (confirmed via direct diff; the sync counterpart in `redis/client.py` gained no type annotation change since it was never annotated). `stubs/redis/redis/asyncio/client.pyi:161` still has `timeout: float = ...`, not `float | None`.
**Trigger:** `await pubsub.get_message(timeout=None)` — upstream's new documented way to "wait indefinitely" — is rejected by a type checker.
**Change:** Change `stubs/redis/redis/asyncio/client.pyi:161`'s `timeout: float = ...` to `timeout: float | None = ...`.
**Priority:** P3 **Action:** consider

### Question — `requirements/submodule-interface-parity-undecidable`
**Why no static evidence could settle it:** The provided `.diff` (`upstream/redis-py-4.3.5...4.4.0.diff`) shows hunks for `redis/commands/bf/commands.py`, `redis/commands/graph/__init__.py`, `redis/commands/graph/commands.py`, `redis/commands/graph/query_result.py`, `redis/commands/redismodules.py`, `redis/commands/search/__init__.py`, and `redis/commands/timeseries/commands.py`, but a direct byte comparison of the two provided tree snapshots shows these exact files are identical between v4.3.5 and v4.4.0. My two authorized offline sources contradict each other and I have no third source or network access to arbitrate. I cannot tell whether these submodules' public interfaces actually changed, so I cannot tell whether the stub's continued silence on `commands/bf/`, `commands/graph/`, `commands/json/`, `commands/redismodules.pyi`, `commands/search/`, `commands/timeseries/` (all untouched by this PR) is correct or a gap.
**What would settle it:** Regenerate or re-fetch a `.diff`/tree pair for these specific paths that agrees with itself (e.g., a fresh `git diff v4.3.5...v4.4.0 -- redis/commands/{bf,graph,json,redismodules,search,timeseries}` run against the real redis-py history), then re-run this sweep.

---

```candidates
### Candidate
id: requirements/redis-init-reexports
axis: Requirements
anchor: stubs/redis/redis/credentials.pyi:3
fix: stubs/redis/redis/__init__.pyi:4
title: Top-level redis/__init__.pyi and asyncio/__init__.pyi miss new 4.4.0 re-exports
claim: Upstream redis/__init__.py 4.4.0 adds CredentialProvider, UsernamePasswordCredentialProvider, default_backoff to __all__ (redis/asyncio/__init__.py adds default_backoff); stubs/redis/redis/__init__.pyi __all__ (lines 4-31) and stubs/redis/redis/asyncio/__init__.pyi __all__ (lines 32-58) contain none of them, and neither file was touched by this PR.
support: Confirmed via `grep CredentialProvider|default_backoff redis-py-4.3.5/redis/__init__.py redis-py-4.4.0/redis/__init__.py` (absent/present) and reading current stubs/redis/redis/__init__.pyi and asyncio/__init__.pyi in full; grepped whole stubs/redis/ tree for CredentialProvider (found in 5 files, not __init__.pyi) and default_backoff (0 hits anywhere).
trigger: `from redis import CredentialProvider` or `from redis import default_backoff`, both valid at runtime and both part of this PR's own feature set, rejected by a type checker.
priority: P1
action: must-fix

### Candidate
id: requirements/redis-retry-accessors
axis: Requirements
anchor: stubs/redis/redis/client.pyi:271
fix: stubs/redis/redis/client.pyi:274
title: Redis/ConnectionPool/RedisCluster miss new get_retry/set_retry/replace_default_node
claim: Upstream 4.4.0 adds Redis.get_retry()/set_retry() (client.py + asyncio/client.py), ConnectionPool.set_retry() (connection.py + asyncio/connection.py), and RedisCluster.get_retry()/set_retry()/replace_default_node() (cluster.py) - all confirmed absent in 4.3.5 via direct def-level tree diff. None of client.pyi, asyncio/client.pyi, connection.pyi, asyncio/connection.pyi, cluster.pyi gained these methods.
support: `diff -u redis-py-4.3.5/... redis-py-4.4.0/...` on each of the 5 upstream files, grep for "def get_retry"/"def set_retry"/"def replace_default_node" pre/post; grepped whole stubs/redis/ tree for all three names, 0 hits.
trigger: `redis_client.get_retry()`, `pool.set_retry(r)`, or `cluster.replace_default_node(node)` - all valid at runtime - rejected by a type checker.
priority: P1
action: must-fix

### Candidate
id: requirements/asyncio-can-read-destructive
axis: Requirements
anchor: stubs/redis/redis/asyncio/connection.pyi:48
fix: (same as anchor)
title: asyncio connection.pyi never gained can_read's 4.4.0 replacement, can_read_destructive
claim: Upstream 4.4.0 renames `async def can_read(self, timeout: float) -> bool` to `async def can_read_destructive(self) -> bool` on BaseParser, PythonParser, HiredisParser, and Connection in redis/asyncio/connection.py. This PR's diff deletes all four can_read stub lines but adds can_read_destructive nowhere in stubs/redis/redis/asyncio/connection.pyi.
support: `diff -u redis-py-4.3.5/redis/asyncio/connection.py redis-py-4.4.0/redis/asyncio/connection.py` filtered to def/class lines shows the four can_read -> can_read_destructive renames; grepped stubs/redis/ tree for can_read_destructive (0 hits) and for can_read in asyncio/ (0 hits, confirming clean removal with no replacement).
trigger: `await connection.can_read_destructive()`, the method ConnectionPool.get_connection actually calls at runtime, rejected by a type checker.
priority: P2
action: consider

### Candidate
id: requirements/backoff-default-backoff
axis: Requirements
anchor: stubs/redis/redis/backoff.pyi:16
fix: stubs/redis/redis/backoff.pyi:29
title: backoff.pyi misses new DEFAULT_CAP, DEFAULT_BASE, default_backoff()
claim: Upstream 4.4.0 adds module-level DEFAULT_CAP = 0.512, DEFAULT_BASE = 0.008, and def default_backoff() to redis/backoff.py (confirmed absent in 4.3.5). stubs/redis/redis/backoff.pyi reflects the cap/base default-value change (met) but has none of these three new names.
support: `grep DEFAULT_CAP|DEFAULT_BASE|default_backoff redis-py-4.3.5/redis/backoff.py redis-py-4.4.0/redis/backoff.py` (absent/present); read stubs/redis/redis/backoff.pyi in full, confirmed absence; grepped whole stubs/redis/ tree for default_backoff, 0 hits.
trigger: `from redis.backoff import default_backoff` or `redis.backoff.DEFAULT_CAP`, valid at runtime, rejected by a type checker.
priority: P2
action: consider

### Candidate
id: requirements/bitfield-ro
axis: Requirements
anchor: stubs/redis/redis/commands/core.pyi:10
fix: stubs/redis/redis/commands/core.pyi:290
title: commands/core.pyi misses the new bitfield_ro command
claim: Upstream 4.4.0 adds `def bitfield_ro(self, key, encoding, offset, items=None) -> ResponseT` to BasicKeyCommands in redis/commands/core.py (confirmed absent in 4.3.5, present in 4.4.0, via def-level tree diff). stubs/redis/redis/commands/core.pyi was touched by this PR (StreamIdT fix) but bitfield_ro is absent from both sync and async mixins.
support: `diff -u redis-py-4.3.5/redis/commands/core.py redis-py-4.4.0/redis/commands/core.py` filtered to def-lines shows "+def bitfield_ro("; grepped stubs/redis/ tree for bitfield_ro, 0 hits; read stubs/redis/redis/commands/core.pyi lines 288-400 confirming only `bitfield` (not `bitfield_ro`) present.
trigger: `redis_client.bitfield_ro(key, "u8", "#0")`, a valid new 4.4.0 command, rejected by a type checker.
priority: P2
action: consider

### Candidate
id: requirements/max-connections-error
axis: Requirements
anchor: stubs/redis/METADATA.toml:2
fix: stubs/redis/redis/exceptions.pyi:42
title: exceptions.pyi misses the new MaxConnectionsError class
claim: Upstream 4.4.0 adds `class MaxConnectionsError(ConnectionError): ...` to redis/exceptions.py - confirmed via `diff -u` on the whole file, the only change in that file between the tags. stubs/redis/redis/exceptions.pyi, untouched by this PR, has no MaxConnectionsError among its 20 exception classes.
support: `diff -u redis-py-4.3.5/redis/exceptions.py redis-py-4.4.0/redis/exceptions.py` (whole-file, unambiguous); read stubs/redis/redis/exceptions.pyi in full. No diff-touched file relates topically to exceptions, so anchored per the ladder's "attach to the change as a whole" fallback at the version-bump line.
trigger: `except redis.exceptions.MaxConnectionsError:`, valid and raised by upstream on pool exhaustion, rejected by a type checker.
priority: P2
action: consider

### Candidate
id: requirements/expiry-t-narrowing
axis: Requirements
anchor: stubs/redis/METADATA.toml:2
fix: stubs/redis/redis/typing.pyi:14
title: typing.pyi's ExpiryT still float | timedelta, not narrowed to int | timedelta
claim: Upstream 4.4.0 changes `ExpiryT = Union[float, timedelta]` to `ExpiryT = Union[int, timedelta]` in redis/typing.py - confirmed via diff, the only change in that file between the tags. stubs/redis/redis/typing.pyi, untouched by this PR, still declares `ExpiryT: TypeAlias = float | timedelta`, and ExpiryT is used by reference throughout commands/core.pyi's expire/setex/getex-family signatures.
support: `diff -u redis-py-4.3.5/redis/typing.py redis-py-4.4.0/redis/typing.py` (whole-file); grepped stubs/redis/ tree for ExpiryT, single hit at typing.pyi:14. No diff-touched file relates to typing.pyi, anchored at the version-bump line per the ladder fallback.
trigger: `redis_client.expire(key, 1.5)`, a float the stub still accepts via ExpiryT, no longer matches what upstream's own 4.4.0 annotations declare acceptable.
priority: P2
action: consider

### Candidate
id: requirements/get-message-timeout-none
axis: Requirements
anchor: stubs/redis/redis/asyncio/client.pyi:87
fix: stubs/redis/redis/asyncio/client.pyi:161
title: async PubSub.get_message's timeout not widened to float | None
claim: Upstream 4.4.0 changes async PubSub.get_message's signature from `timeout: float = 0.0` to `timeout: Optional[float] = 0.0` in redis/asyncio/client.py (confirmed via diff; the sync counterpart gained no annotation change since it was never annotated). stubs/redis/redis/asyncio/client.pyi:161 still has `timeout: float = ...`.
support: `grep -A2 "def get_message" redis-py-4.3.5/redis/asyncio/client.py redis-py-4.4.0/redis/asyncio/client.py` shows the Optional[float] change; read stubs/redis/redis/asyncio/client.pyi:161. Anchored at the nearest diff-touched line in the same file (the `blocking` param added to lock(), line 87), since get_message itself was not touched by this PR's diff.
trigger: `await pubsub.get_message(timeout=None)`, upstream's documented way to wait indefinitely as of 4.4.0, rejected by a type checker.
priority: P3
action: consider
```

```ledger
redis/__init__.pyi and asyncio/__init__.pyi miss new __all__ entries CredentialProvider/UsernamePasswordCredentialProvider/default_backoff | grep whole stub tree for the 3 new names | stubs/redis/redis/credentials.pyi:3 | candidate
Redis/ConnectionPool/RedisCluster miss new get_retry/set_retry/replace_default_node | grep whole stub tree for the 3 new names | stubs/redis/redis/client.pyi:271 | candidate
asyncio connection.pyi never gained can_read_destructive after can_read was removed | grep whole stub tree for can_read_destructive | stubs/redis/redis/asyncio/connection.pyi:48 | candidate
backoff.pyi misses new DEFAULT_CAP/DEFAULT_BASE/default_backoff | grep whole stub tree for default_backoff | stubs/redis/redis/backoff.pyi:16 | candidate
commands/core.pyi misses new bitfield_ro command | grep whole stub tree for bitfield_ro | stubs/redis/redis/commands/core.pyi:10 | candidate
exceptions.pyi misses new MaxConnectionsError | grep whole stub tree for MaxConnectionsError | stubs/redis/METADATA.toml:2 | candidate
typing.pyi's ExpiryT not narrowed from float to int | diff redis/typing.py 4.3.5 vs 4.4.0 | stubs/redis/redis/typing.pyi:14 | candidate
async PubSub.get_message timeout not widened to float-or-None | diff redis/asyncio/client.py 4.3.5 vs 4.4.0 get_message | stubs/redis/redis/asyncio/client.pyi:161 | candidate
bf/graph/json/redismodules/search/timeseries submodule parity with 4.4.0 is undecidable | diff -rq the two provided tree snapshots for these 6 files | upstream/redis-py-4.4.0/redis/commands/graph/__init__.py:12 | question
get_node_name's port param already str-or-int, matching upstream's widened type | diff redis/cluster.py 4.3.5 vs 4.4.0 get_node_name | stubs/redis/redis/cluster.pyi:16 | acquitted
smembers's return type already set[_StrType], matching upstream's Set | diff redis/commands/core.py 4.3.5 vs 4.4.0 smembers | stubs/redis/redis/commands/core.pyi:769 | acquitted
lmpop missing from stub is pre-existing since 4.3.5, unrelated to this version-bump delta | diff lmpop def between 4.3.5 and 4.4.0 sources | upstream/redis-py-4.3.5/redis/commands/core.py:2534 | acquitted
TDigestCommands trimmed_mean/rank/revrank/byrank/byrevrank already present at 4.3.5, unchanged going into 4.4.0 | python diff of TDigestCommands method list 4.3.5 vs 4.4.0 | upstream/redis-py-4.3.5/redis/commands/bf/commands.py:356 | acquitted
utils.py warn_deprecated/deprecated_function already existed at 4.3.5, unchanged into 4.4.0 | diff redis/utils.py 4.3.5 vs 4.4.0 | upstream/redis-py-4.3.5/redis/utils.py:85 | acquitted
EXCEPTION_CLASSES new error-string keys (WRONGPASS, NO_AUTH_SET_ERROR) need no stub change, attribute is typed generically | check stub type annotation | stubs/redis/redis/connection.pyi:32 | acquitted
SentinelManagedConnection.read_response type:ignore[override] correctly matches upstream's un-widened override signature | compare SentinelManagedConnection.read_response to base Connection.read_response | upstream/redis-py-4.4.0/redis/asyncio/sentinel.py:66 | acquitted
asyncio Lock.redis narrowed to Redis[Any] though upstream 4.4.0 widens to Union[Redis, RedisCluster]; fix blocked by asyncio.cluster being wholly unstubbed | diff redis/asyncio/lock.py 4.3.5 vs 4.4.0 __init__ | stubs/redis/redis/asyncio/lock.pyi:26 | observation
credentials.pyi marks CredentialProvider.get_credentials @abstractmethod though the stubbed class has no ABC base | read stubs/redis/redis/credentials.pyi | stubs/redis/redis/credentials.pyi:4 | observation
```

```manifest
stubs/redis/METADATA.toml | reviewed | version bump 4.3.5->4.4.0 verified correct against both upstream METADATA equivalents (package version)
stubs/redis/redis/asyncio/client.pyi | reviewed | credential_provider, lock's blocking param, Pipeline.xautoclaim StreamIdT all verified met; get_retry/set_retry and get_message timeout gaps found (candidates 2, 8)
stubs/redis/redis/asyncio/connection.pyi | reviewed | credential_provider, disconnect(nowait), read_response(timeout), SocketBuffer/NONBLOCKING_* removal, HiredisParser.read_from_socket all verified met; can_read_destructive and ConnectionPool.set_retry gaps found (candidates 2, 3)
stubs/redis/redis/asyncio/sentinel.pyi | reviewed | read_response type:ignore[override] verified as correctly matching upstream's un-widened override
stubs/redis/redis/backoff.pyi | reviewed | cap/base defaults verified met; DEFAULT_CAP/DEFAULT_BASE/default_backoff gap found (candidate 4)
stubs/redis/redis/client.pyi | reviewed | credential_provider verified met; get_retry/set_retry gap found (candidate 2); lock's pre-existing blocking param confirmed unaffected
stubs/redis/redis/cluster.pyi | reviewed | retry param and __nonzero__ removal verified met; get_retry/set_retry/replace_default_node gap found (candidate 2)
stubs/redis/redis/commands/core.pyi | reviewed | xautoclaim StreamIdT fix (sync+async) verified met; bitfield_ro gap found (candidate 5)
stubs/redis/redis/connection.pyi | reviewed | credential_provider verified met; ConnectionPool.set_retry gap found (candidate 2); can_read left correctly unchanged (sync wasn't renamed upstream)
stubs/redis/redis/credentials.pyi | reviewed | new file's CredentialProvider/UsernamePasswordCredentialProvider interface verified to match upstream's new redis/credentials.py
```

```counts
met=12 not-met=8 unverifiable=1
```
````

### 4.3 Verifier

**Model:** `claude-sonnet-5` (`model: "sonnet"` on the `Agent` call). Fresh context — no prior conversation with either finder, no `support` fields (mechanically stripped by `scripts/build_verifier_prompt.py`).

**Prompt (verbatim, as given to the sub-agent):**

> You are the fresh-context verifier for a code review of python/typeshed#9458 (the redis 4.4.0 stub bump in the python/typeshed repository). You have NOT seen any finder's reasoning, process, or confidence — only their claims. This is deliberate.
>
> First, read your brief in full: /tmp/holdout/skills/panel/references/verify.md — it defines confirmed/plausible/refuted, the asymmetry (default to plausible), deduplication rules, and priority/action recalibration rules.
>
> Then read your verifier prompt in full: /tmp/holdout/work/c/panel-seed1/verifier-prompt.md — it contains the pinned run identity (base SHA, head SHA, merge-base, all equal to the merge-base since the base branch moved before merge — see the file) and 9 candidates (their `support` fields have been mechanically stripped; you only have claim, trigger, priority, action). Rule on every one of the 9 candidates.
>
> The repository to check candidates against is the git clone at /tmp/holdout/runs/c/panel-seed1 (local branch `main` = merge-base = base SHA in the prompt; local branch `review-head` = head SHA in the prompt; the working tree is currently checked out at review-head). You also have read access to two upstream reference trees that these typeshed stubs describe, at /tmp/holdout/packets/c/upstream/redis-py-4.3.5/ and /tmp/holdout/packets/c/upstream/redis-py-4.4.0/ (the actual redis-py library source at those two tags) — use these to check whether a claimed upstream signature, rename, or addition is real. There is also a GitHub compare .diff at /tmp/holdout/packets/c/upstream/redis-py-4.3.5...4.4.0.diff, but be aware it has been found to disagree with the tree snapshots for at least these 7 files: redis/commands/bf/commands.py, redis/commands/graph/__init__.py, redis/commands/graph/commands.py, redis/commands/graph/query_result.py, redis/commands/redismodules.py, redis/commands/search/__init__.py, redis/commands/timeseries/commands.py (the .diff shows hunks for all seven; the tree snapshots are byte-identical between the two tags for all seven). Trust the tree-snapshot comparison over the .diff file where they conflict.
>
> Operating constraints, binding on you:
> 1. Offline — no network tool of any kind (no fetch, no gh, no curl-equivalent).
> 2. No execution — do not run python, mypy, pyright, stubtest, pre-commit, flake8, or any test/lint/build command. Static reasoning only; you may run a single focused read/grep/diff, not a build or test.
> 3. Clone hygiene — do not run git checkout, git switch, git reset, git stash, or anything else that mutates the working tree at /tmp/holdout/runs/c/panel-seed1. Read-only git commands (git show, git diff, git log, git blame, git ls-tree) are fine, but do not read history beyond the pinned head (55dfb451101480275ae05f2f08d1a899a691a77d) — report explicitly, in your reply, which git history commands you ran, if any.
> 4. Stay in your sandbox: the clone at /tmp/holdout/runs/c/panel-seed1, the skill snapshot at /tmp/holdout/skills/panel/, and the packet directory at /tmp/holdout/packets/c/ (including upstream/). Report explicitly if you read anything outside these.
> 5. No session relays — finish entirely in this one turn, do not stop to ask anything.
>
> Return, as your final message, exactly what verify.md's "What to return" section specifies: per candidate its id, verdict (confirmed/plausible/refuted), one sentence of justification, the quoted line supporting confirmed/refuted verdicts, any corrected trigger, and priority/action with a note if you moved either — then the merge list (which ids you collapsed into which, applying the "keep the Requirements one when Code and Requirements describe the same defect" rule where applicable), the counts by verdict, and any observations (accurate asides outside your mandate to verdict, one sentence plus one file:line pointer each).

The verifier prompt file (`/tmp/holdout/work/c/panel-seed1/verifier-prompt.md`) was built by `scripts/build_verifier_prompt.py --brief references/verify.md --repo /tmp/holdout/runs/c/panel-seed1 --base-sha 8365b1aaefd46d506ca0dfe73e9721da2d03c566 --head-sha 55dfb451101480275ae05f2f08d1a899a691a77d --merge-base 8365b1aaefd46d506ca0dfe73e9721da2d03c566 --code finder-code.md --requirements finder-requirements.md` — exit 0, no `## Related acquitted ledger rows` section (verify.md carries no `## Related acquittals` heading, so the script correctly omitted it), 9 `### Candidate` sections carrying every field except `support` (spot-checked by grepping the output for the string `support:` — zero matches, confirming the strip worked).

**Verbatim report:**

> ## Verification Report — python/typeshed#9458 (redis 4.4.0 stub bump)
>
> **Compliance notes (per operating constraints):** Git commands run were all read-only and did not exceed the pinned head (`55dfb4511`): `git log --oneline -1 HEAD`, `git branch -v`, `git status`, `git diff main..review-head --stat`, `git diff main..review-head`, `git show main:stubs/redis/redis/asyncio/connection.pyi`. No history beyond the pinned head was read. Files read: the clone at `/tmp/holdout/runs/c/panel-seed1`, the two upstream trees under `/tmp/holdout/packets/c/upstream/`, `/tmp/holdout/skills/panel/references/verify.md`, and `/tmp/holdout/work/c/panel-seed1/verifier-prompt.md` (the last is outside the strict sandbox list of clone/skill/packets, but was explicitly named as required reading in the task instructions, so I read it). No other paths were touched. No execution tools were used — static `grep`/`diff`/`sed` reads only.
>
> ### Candidate 1 — code/asyncio-connection-pyi/missing-can-read-destructive
> **Verdict: CONFIRMED.** Upstream 4.4.0 renames `can_read`→`can_read_destructive` on `BaseParser`/`PythonParser`/`HiredisParser`/`Connection` (`redis/asyncio/connection.py:199,231,344,776`), and it is called as normal operation in `ConnectionPool.get_connection` (lines 1369, 1374); the stub deletes every `can_read` line and adds `can_read_destructive` nowhere. Quoted line: upstream `redis/asyncio/connection.py:776` `async def can_read_destructive(self):` — absent by name anywhere in `stubs/redis/redis/asyncio/connection.pyi`. Priority P1 (kept). Action must-fix (kept) — merges into Candidate 4 below.
>
> ### Candidate 2 — requirements/redis-init-reexports
> **Verdict: CONFIRMED.** Upstream 4.4.0 adds `CredentialProvider`, `UsernamePasswordCredentialProvider`, `default_backoff` to `redis/__init__.py`'s `__all__` (and `default_backoff` to `redis/asyncio/__init__.py`'s), but neither stub `__init__.pyi` was touched by this PR. Quoted line: upstream `redis/__init__.py:67` `"CredentialProvider",` — no corresponding entry anywhere in the stub. Priority P1 (kept, real import failure on this PR's own headline feature). Action must-fix (kept).
>
> ### Candidate 3 — requirements/redis-retry-accessors
> **Verdict: CONFIRMED.** `get_retry`/`set_retry` and `replace_default_node` are all absent from 4.3.5 and present in 4.4.0 across five upstream files; grep for these three names across the five corresponding stub files returns nothing. Quoted line: upstream `redis/cluster.py:382` `def replace_default_node(self, target_node: "ClusterNode" = None) -> None:` — no match in the stub. Priority P1 (kept). Action must-fix (kept).
>
> ### Candidate 4 — requirements/asyncio-can-read-destructive
> **Verdict: CONFIRMED.** Same defect and same evidence as Candidate 1. Quoted line: same as Candidate 1. Priority **P2 → P1** (raised, matching the merge — this is a full removal of documented async API with no replacement, not a mere stylistic gap). Action **consider → must-fix** (raised for the same reason).
>
> ### Candidate 5 — requirements/backoff-default-backoff
> **Verdict: CONFIRMED.** `DEFAULT_CAP`/`DEFAULT_BASE`/`default_backoff()` are new in 4.4.0, unrestricted by any `__all__`, and absent from the stub. Quoted line: upstream `redis/backoff.py:113` `def default_backoff():` — no match in the stub. Priority P2 (kept). Action consider (kept).
>
> ### Candidate 6 — requirements/bitfield-ro
> **Verdict: CONFIRMED.** `def bitfield_ro(...)` is added to `BasicKeyCommands` in 4.4.0 (absent 4.3.5, confirmed at line 1507), absent from the stub's sync and async mixins. Quoted line: upstream `redis/commands/core.py:1507` `def bitfield_ro(` — no match in the stub. Priority P2 (kept). Action consider (kept).
>
> ### Candidate 7 — requirements/max-connections-error
> **Verdict: CONFIRMED.** `diff -u redis/exceptions.py` shows exactly one hunk between tags, adding `class MaxConnectionsError(ConnectionError): ...`; the stub's 20 exception classes do not include it. Quoted line: upstream `redis/exceptions.py:204` `class MaxConnectionsError(ConnectionError):` — absent from the stub. Priority P2 (kept). Action consider (kept). Note: anchor `stubs/redis/METADATA.toml:2` doesn't exist (file is a single line); does not affect the verdict — the true defect site (`exceptions.pyi:42`) checks out exactly. See Observations.
>
> ### Candidate 8 — requirements/expiry-t-narrowing
> **Verdict: CONFIRMED.** `diff -u redis/typing.py` shows exactly one hunk: `Union[float, timedelta]` → `Union[int, timedelta]`; the stub is unchanged by this PR. Quoted line: `stubs/redis/redis/typing.pyi:14` `ExpiryT: TypeAlias = float | timedelta` vs. upstream `redis/typing.py:19` `ExpiryT = Union[int, timedelta]`. Priority P2 (kept). Action consider (kept) — a stub-too-permissive mismatch rather than a call-rejection, consistent with the lower action. Note: anchor `stubs/redis/METADATA.toml:2` also doesn't exist; same non-effect as Candidate 7.
>
> ### Candidate 9 — requirements/get-message-timeout-none
> **Verdict: CONFIRMED.** Upstream 4.4.0 `redis/asyncio/client.py:896` changes `timeout: float = 0.0` to `timeout: Optional[float] = 0.0`, with a real behavior change (`block=(timeout is None)` at line 905); the stub at line 161 is unchanged. Quoted line: `stubs/redis/redis/asyncio/client.pyi:161` `async def get_message(self, ignore_subscribe_messages: bool = ..., timeout: float = ...): ...`. Priority P3 (kept). Action consider (kept).
>
> ### Merge list
> **1 → 4**: Candidate 1 (Code) and Candidate 4 (Requirements) describe the identical defect (missing `can_read_destructive`). Kept Candidate 4 (Requirements framing, carries the issue-vs-diff citation), with the merged priority/action raised to the higher of the two inputs (P1 / must-fix, from Candidate 1).
>
> No other pair shares a fix: Candidates 2 and 5 are related (both touch `default_backoff`) but are not duplicates — fixing 2's re-export alone would still fail because `default_backoff` doesn't exist in `backoff.pyi` to import (Candidate 5's gap), and fixing 5 alone would still leave `from redis import default_backoff` unresolved (Candidate 2's gap). Both must be fixed independently, so both are kept.
>
> ### Counts by verdict
> Confirmed: 9. Plausible: 0. Refuted: 0. (9 candidates, 1 merge → 8 surviving distinct findings.)
>
> ### Observations
> - `stubs/redis/redis/asyncio/sentinel.pyi:18` — this PR added a `# type: ignore[override]` comment to `SentinelManagedConnection.read_response` rather than updating its signature to match the base `Connection.read_response`'s new `timeout` parameter, silencing rather than resolving the Liskov mismatch introduced by this same diff.
> - `stubs/redis/METADATA.toml:1` — the file is exactly one line long; the anchor `stubs/redis/METADATA.toml:2` cited by Candidates 7 and 8 points past end-of-file. This is an anchor-placement inaccuracy only (per brief, "judge the defect, not the anchor") and does not affect either candidate's verdict, since both candidates' actual fix-site quotes (`exceptions.pyi:42`, `typing.pyi:14`) are exact.

**What I did with this on return:** validated the two "anchor doesn't exist" flags myself (`wc -l stubs/redis/METADATA.toml` → 1), confirmed both candidates' real anchors had no honest diff-touched, topically-related line at all (not just a wrong line number) by checking `git diff main review-head --unified=0` against `exceptions.pyi` and `typing.pyi` (neither file appears in that output — the PR never touches either), and moved both findings to the review body with no line anchor rather than merely correcting the line number to `:1`, since `:1` (the version-bump line) is exactly as topically unrelated as `:2` was. I independently spot-checked 5 of the 9 confirmations myself (§ 1, § 10) before accepting them.

## 5. Everything consulted beyond the diff

**My own reads/commands** (all repo-wide where noted; all case-insensitive where a grep is named as such — plain `grep`/`git diff`/`git show`/`diff` used below were exact-string or line-diff tools, not text searches needing case-folding, so "case-insensitive" doesn't apply to them; where I did run a text search I say so):

- `find /tmp/holdout/skills/panel -type f | sort` — enumerated the skill snapshot.
- Read in full: `SKILL.md`, `references/finding-format.md`, `references/code-axis.md`, `references/requirements-axis.md`, `references/verify.md`, `references/publishing.md`, `scripts/build_shared_block.py`, `scripts/build_verifier_prompt.py`, `scripts/link_coordinate.py`, `scripts/validate_finder_report.py` (not repo-wide searches — direct file reads).
- Read in full: `/tmp/holdout/packets/c/packet.md`.
- `git -C /tmp/holdout/runs/c/panel-seed1 status`, `branch -v`, `log --oneline -3 main`, `log --oneline -5 review-head`, `diff main review-head --stat`, `diff main review-head` (full), `rev-parse review-head`, `rev-parse main`, `merge-base review-head main`, `cat-file -t 70025c372346288675437fc0bd273db84cc0b3d5`, `log --oneline --all | head -5`, `rev-list --all | wc -l`, `diff main review-head --unified=0` (touched-line-only diff, used to validate every finding's anchor at publish time), `show main:CONTRIBUTING.md` (×2, paginated), `show main:stubs/redis/redis/credentials.pyi` (implicitly via file reads post-checkout, not a separate `git show` call — the working tree is already at `review-head`).
- `git -C /tmp/holdout/runs/c/panel-seed1 diff main review-head --name-status` → `/tmp/holdout/work/c/panel-seed1/manifest.tsv` (the changed-file manifest fed to `validate_finder_report.py`).
- `python3 scripts/build_shared_block.py ...` (§ 6) and `python3 scripts/build_verifier_prompt.py ...` (§ 4.3) — both exit 0.
- `python3 scripts/validate_finder_report.py --axis code ...` — run twice (fail, then pass after re-dispatch); `python3 scripts/validate_finder_report.py --axis requirements ...` — run twice (fail, then pass after re-dispatch).
- `python3 scripts/link_coordinate.py render ...` — run 17 times, once per coordinate fragment needed for the payload (§ "rendering the payload" below); `python3 scripts/link_coordinate.py check ...` — run 3 times, spot-checking the three line-comment anchors' rendered fragments against the rule (all passed, exit 0).
- Independent verification of 5 of the verifier's 9 confirmations, directly against the upstream trees and the stub (not repo-wide searches, targeted `grep -n`/`diff -u` on named files): `grep -n "def replace_default_node\|def get_retry\|def set_retry" redis-py-4.3.5/redis/cluster.py redis-py-4.4.0/redis/cluster.py`; `diff -u redis-py-4.3.5/redis/exceptions.py redis-py-4.4.0/redis/exceptions.py`; `grep -n "def get_message" -A3 redis-py-4.3.5/redis/asyncio/client.py redis-py-4.4.0/redis/asyncio/client.py`; `grep -n "can_read" /tmp/holdout/runs/c/panel-seed1/stubs/redis/redis/asyncio/connection.pyi`; `grep -n "CredentialProvider\|default_backoff" /tmp/holdout/runs/c/panel-seed1/stubs/redis/redis/__init__.pyi /tmp/holdout/runs/c/panel-seed1/stubs/redis/redis/asyncio/__init__.pyi`.
- Independent verification of the Requirements finder's `.diff`-file-vs-tree-snapshot contradiction (§ 4.2): `diff -q redis-py-4.3.5/<path> redis-py-4.4.0/<path>` for each of the 7 files the `.diff` shows hunks for (all identical); `grep -c "^diff --git a/redis/commands/bf/commands.py" redis-py-4.3.5...4.4.0.diff`; `grep -n "^diff --git" redis-py-4.3.5...4.4.0.diff | grep -E "bf/commands|graph/__init__|graph/commands|graph/query_result|redismodules|search/__init__|timeseries/commands"` (this grep's second stage is a case-sensitive, but not repo-wide, filter over the diff's own header lines — not a search of the codebase); `sed -n '7686,7720p'` on the `.diff` file to read one of the contradicting hunks; `grep -n "TDIGEST_TRIMMED_MEAN\|deprecated_function" redis-py-4.3.5/redis/commands/bf/commands.py redis-py-4.4.0/redis/commands/bf/commands.py`; `grep -rn "__version__" redis-py-4.3.5/redis/__init__.py redis-py-4.4.0/redis/__init__.py`; `cat redis-py-4.3.5/setup.py redis-py-4.4.0/setup.py | grep -i version` (confirmed the tree snapshots are genuinely tagged 4.3.5/4.4.0 by their own `setup.py`, ruling out "wrong tree" as the explanation).
- Anchor-validation reads for the publish step (§ 10): `sed -n` over `stubs/redis/redis/client.pyi`, `stubs/redis/redis/asyncio/connection.pyi`, `stubs/redis/redis/asyncio/client.pyi`, `stubs/redis/redis/backoff.pyi`, `stubs/redis/redis/exceptions.pyi`, `stubs/redis/redis/typing.pyi`, `stubs/redis/redis/commands/core.pyi`, `stubs/redis/redis/credentials.pyi`, `stubs/redis/redis/asyncio/lock.pyi`; `wc -l stubs/redis/redis/backoff.pyi stubs/redis/redis/exceptions.pyi`; upstream `grep -n "class Lock\|def __init__\|redis:" redis-py-4.3.5/redis/asyncio/lock.py redis-py-4.4.0/redis/asyncio/lock.py`.

**Both finders' own consulted material** is recorded in their manifests (§ 4.1, § 4.2) and in their ledgers' "falsification route" and "decisive evidence" columns (§ 3) — both read every one of the 10 changed files, both read across into the two upstream trees extensively (dozens of targeted `grep`/`diff` calls per their own `support` fields, stripped from the verifier prompt but visible in their full reports at § 4.1/§ 4.2), and both swept the whole `stubs/redis/` tree (Code finder) or the whole stub tree plus, in one case, the diff-vs-tree-snapshot cross-check (Requirements finder) case-insensitively for retired/new vocabulary, as their briefs require. Neither finder's manifest records a file it could not read; neither reported an abandoned check.

## 6. The "context" digest and its inputs

Not applicable — see § 1 above. No such artifact exists in this skill. What this skill does compute once and reuse everywhere is the **pinned run identity** (base/head/merge-base triple) and the **shared block** built once by `scripts/build_shared_block.py` and reused byte-identical as the leading prefix of both finder prompts (verified with a `diff` of the two prompts' first 988 lines — identical). Inputs to the shared block: `--repo /tmp/holdout/runs/c/panel-seed1 --base-ref main --base-sha 8365b1aaefd46d506ca0dfe73e9721da2d03c566 --head-sha 55dfb451101480275ae05f2f08d1a899a691a77d --merge-base 8365b1aaefd46d506ca0dfe73e9721da2d03c566 --finding-format /tmp/holdout/skills/panel/references/finding-format.md` (no `--suite-results`: run conditions forbid execution, so no test suite was run in step 1). Exit code 0, no stderr notice (diff was well under the 200,000-byte fallback threshold). The PR's title, body (`Closes #9329`), issue coordinates (`python/typeshed#9329`), and `comments_available: true` were taken verbatim from the packet (§§1, 3, 4) and are reproduced in full inside the Requirements finder's axis-specific block (not part of the shared block, which is axis-neutral); see `/tmp/holdout/work/c/panel-seed1/requirements-axis-block.md`. The guidance list resolved by the script is `CONTRIBUTING.md` only (root), blob `102199c8a6b127a4da6e9d575b2e3a677ed21127` — matching the packet's §7 table exactly (`AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `CODEOWNERS`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/pull_request_template.md` all absent, confirmed by the script's own `ls-tree` sweep over the base tree, not just by trusting the packet).

## 7. Mechanism checklist

- **Question channel:** fired once, at the finder level — the Requirements finder's `requirements/submodule-interface-parity-undecidable` came from its own "cannot tell from the code" bucket (`references/requirements-axis.md` § Step 2) and was routed straight to publication as a question, bypassing the verifier entirely (`references/verify.md`: "One class of item never goes to the verifier"). Demonstrated in § 4.2's finder report (the "### Question" section) and § 3's ledger (disposition `question`). No `plausible` verdict occurred, so the verifier-driven question path (`verify.md`: "plausible becomes a question") did not additionally fire this run — did not fire.
- **Clean-verdict or related-acquittal verification:** the verifier prompt built by `scripts/build_verifier_prompt.py` had no `## Related acquitted ledger rows` section, because `references/verify.md` carries no `## Related acquittals` heading for the script to match against (confirmed by `grep -n "Related" references/verify.md` — zero hits). This is a property of this skill pin, not a run failure: the mechanism the script supports is present in the code but not invoked by this skill's verify brief. Neither finder returned zero candidates, so the "finders that return no candidates... skip it" shortcut (`SKILL.md` step 3) also did not apply — the verifier ran on all 9 candidates. No re-open occurred (first review, nothing to reopen).
- **Observations:** fired at all three levels — Code finder (1), Requirements finder (2), verifier (2, one of which I chose not to publish — § 10). Pooled and deduplicated by me at step 4 per `publishing.md` § The summary ("Pool the finders' observations with the verifier's and deduplicate the pool... before the cap applies"): 5 raw → 1 duplicate pair merged → 4 candidates for publication → 1 excluded as non-code-fact (§ 10) → 3 published, exactly at the cap, 0 dropped for exceeding it. Demonstrated in § 1's Observations bullet, § 3's ledger, and the payload's `## Observations` section.
- **Fix-sufficiency check on any concurrency/invariant candidate:** did not fire — no candidate in this run concerned concurrency or a stated invariant (the whole diff is type-stub signature work; the closest thing to an invariant candidate, the `can_read`/`can_read_destructive` rename, is a naming/typing gap, not a concurrency or invariant claim, and the verifier's confirmation for it cites a quoted upstream line and a quoted call site rather than an interleaving argument). Correctly did not fire.
- **Follow-up verifier round:** did not fire — this is a first review with no prior findings, so `verify.md` § "Prior findings, on a re-review" never triggers, and no candidate came back from the single verifier round needing a second pass (no `plausible` verdicts, which are the only thing that would create a live thread for a hypothetical follow-up). Did not fire, correctly (nothing in this skill pin's contract calls for an automatic second verifier round beyond re-review situations).
- **Deferral handling:** I searched the packet's full prior-review record (§ 6 of `packet.md`: 2 review submissions, 1 review thread, 17 non-review comments, all reproduced verbatim in the Requirements finder's axis-specific block) for any comment that explicitly postpones a design/naming/API-shape decision on unreleased public surface. Found none — the closest candidates (the rebase-policy exchange, the `read_response`/`timeout` stubtest-failure discussion) are process and troubleshooting, not deferrals, and I said so explicitly in the Requirements finder's prompt (`requirements-axis-block.md`, "§ Explicit deferrals from the pull request's review comments"). This is a judgment call — see § 10. Since no deferral exists, the Requirements axis is not held at `Waiting for information` by this mechanism; it is `Findings` on its own merits (8 not-met-adjacent findings survive).
- **Retrospective mode:** fired throughout — the `Mode` line is the payload's first line, publication was treated as disabled end-to-end (nothing was posted; steps that would post instead rendered and stopped, per the dispatch's rule 2 and `SKILL.md`'s "run the whole pipeline, but publication is disabled"), and the run identity/status derivation both proceeded exactly as they would for an open pull request, event `COMMENT`, per the dispatch's explicit instruction. Demonstrated in the payload's first line and its `**Changes Requested (advisory)**` status line (advisory because `kamui` is not authorized to gate merge on an already-merged PR, and `Incomplete`/`Needs Information` have no gating form regardless).

## 8. History discipline

I ran, in the clone `/tmp/holdout/runs/c/panel-seed1`: `git status`, `git branch -v`, `git log --oneline -3 main`, `git log --oneline -5 review-head`, `git diff main review-head --stat`, `git diff main review-head` (full), `git rev-parse review-head`, `git rev-parse main`, `git merge-base review-head main`, `git cat-file -t 70025c372346288675437fc0bd273db84cc0b3d5` (probing whether the PR-recorded base SHA is reachable — it is not, confirming the packet's note that only the merge-base is locally available), `git log --oneline --all | head -5`, `git rev-list --all | wc -l` (confirming the truncated history's total object count, 7407 commits, and that its newest entry is still the pinned head `55dfb4511`), and `git show main:CONTRIBUTING.md` (twice, paginated). I did not run `git log` past the pinned head, did not fetch, and did not attempt to reach `70025c372346288675437fc0bd273db84cc0b3d5` beyond the one `cat-file -t` probe that confirmed it is absent. No sub-agent I dispatched was authorized to run history-mutating or network commands (see their operating-constraints sections), and each was required to report explicitly whether it read history beyond the pinned head.

## 9. Sandbox disclosure

One path outside the nominal sandbox list (clone / skill snapshot / packet directory / my own work-report-payload paths) was read, by design and necessity: `/tmp/holdout/work/c/panel-seed1/` itself — my own work directory — which the dispatch names as "your working directory for payload JSON, scratch files, and script output" (dispatch § Files), so it is in-sandbox, not an exception; I list it here only because it is not one of the four categories the dispatch's rule 6 names verbatim (clone, skill snapshot, packet directory, and "your work, payload, and report paths" — the work directory falls under the last of those, quoted directly from rule 6, so this is not actually a violation, just a clarification that I read/wrote there constantly). The verifier sub-agent explicitly flagged that it read `/tmp/holdout/work/c/panel-seed1/verifier-prompt.md` (§ 4.3) as technically outside the four categories I gave it in its own operating-constraints paragraph (which listed only clone/skill/packet, omitting the work directory by my oversight in that sub-agent's prompt) — it read it anyway because I had explicitly told it to as "your verifier prompt" in the same message, and it disclosed the tension rather than silently resolving it. I judge this a wording gap in the sub-agent prompt I wrote, not a genuine sandbox breach: the file is mine, in my own work directory, written by me for exactly this purpose. No sub-agent read any other run's clone, report, or payload (all three sub-agents' prompts named only this cell's paths, and none reported reading anything else). I read no path outside the clone, the skill snapshot, the packet directory (including its `upstream/` subtree), and my own work/report/payload paths.

## 10. Notes

**Review payload:** rendered in full at `/tmp/holdout/reports/c/panel-seed1-payload.md` — the summary body (with the `Mode` line, status, per-axis outcome, run identity, coverage, the required short paragraph, the index, counts, `## Observations`, `## Open questions`, and the `<!-- review-run ... -->` trailer), the three findings that would be separate line comments (reproduced in full a second time under "## Line comments" to show exactly what would attach to their specific anchors, since nothing was actually posted and there is no PR comment thread to point to instead), and the five body-only findings' full text inline in the body itself, per `finding-format.md`'s anchor ladder rule 1/4 worked example. Nothing else is in that file.

**Every judgment call made on an ambiguity in the skill's contract, and why:**

1. **"Context digest" (dispatch rule 3) does not exist in this skill.** I searched exhaustively (`grep -rn -i "digest"` over the entire skill snapshot, zero hits) and concluded this instruction, which is boilerplate shared across the evaluation's cells, targets a different skill (`legacy reviewer`, which has such a concept) and is inapplicable to the Panel line (`code-review-deep-publish`). I treated the pinned run identity (base/head/merge-base) and the once-built, byte-reused shared block as the closest actual analog and computed each exactly once, as the dispatch's spirit ("compute it once") would require of whatever this skill does have. Guidance used: the skill's own text is authoritative over a cross-cell dispatch template; where they conflict, the skill wins, since dispatch rule 1 itself says "follow your skill as written... do not borrow behavior from any other review skill."
2. **No explicit deferral found in the prior-review record.** I read every one of the 20 prior-review items (2 reviews, 1 thread, 17 comments) myself before handing the Requirements finder my own conclusion ("none found") rather than the raw record alone — the finder's brief only asks it to receive deferrals already found by the reviewer at step 1, not to hunt for them itself from a raw dump. This is explicit in `SKILL.md` step 1's bullet on deferrals and step 2's "Include, verbatim, every explicit deferral... found in the pull request's review comments." I judged the rebase-policy exchange and the `read_response`/`timeout` troubleshooting thread as clearly not deferrals (process and diagnosis, not a postponed design/naming/API-shape decision) rather than referring the judgment to the finder, since the reviewer (me) is the one `SKILL.md` step 1 assigns this task to.
3. **Base SHA for guidance-lookup and shared-block purposes = merge-base, not the PR-recorded base SHA.** The packet is explicit that the two differ and that review proceeds "against the merge-base"; the PR-recorded SHA (`70025c37...`) is confirmed unreachable in this truncated clone (`git cat-file -t` fails on it). I used the merge-base value everywhere `SKILL.md`/its scripts call for a "base SHA," which matches both the packet's own instruction and the only value actually available.
4. **Anchor correction for two merged/multi-file/untouched-file findings, done by me at step 4 rather than by the finders.** `SKILL.md` step 4 explicitly assigns anchor validation to me ("Validate every anchor against the diff before submitting... An anchor that fails validation moves down the ladder to the body, never into a doomed request") and `finding-format.md`'s ladder forbids "attach[ing] it to an unrelated line merely to make it a line comment." Applying this mechanically against `git diff main review-head --unified=0`, I found: (a) the Requirements finder's `can_read_destructive` candidate anchored at `asyncio/connection.pyi:48`, a context line the diff never touches (the touched replacement line for the same defect, on the `Connection` class specifically, is `:135` — the Code finder's own anchor for the same defect) — corrected to `:135`; (b) the retry-accessors, bitfield_ro, max-connections-error, expiry-t-narrowing, and get-message-timeout-none findings' anchors were each on a diff-touched line that is topically unrelated to the claim (an unrelated `credential_provider`/import/`blocking`-param addition in the same file, or `stubs/redis/METADATA.toml:2`, which does not exist — the file is one line long — for the two findings whose named file was never touched by this PR at all) — moved all five to the review body with no line anchor, per the ladder's rule 4 and the worked example in `finding-format.md` § Anchor and fix site ("A finding about a whole file the diff adds or rewrites has no single line: it goes in the review body"; I read "has no honest anchor" as covering "the only touched lines in scope are unrelated to the claim," not only "no lines are touched at all"). I did not alter any finding's claim, trigger, priority, or action to make this correction — only the anchor/line-comment-vs-body placement.
5. **Verifier's second "observation" (the anchor-placement note) was not published as an Observation.** `publishing.md` defines Observations as "an accurate fact that failed the finding bar," "stating what is, never what should be," about the code. The verifier's note is about my own review construction (an anchor I built pointing past end-of-file), not a fact about `stubs/redis/`. I treated it as a directive to fix (which I did, per point 4 above) rather than content to publish, and recorded it in § 3's "Verifier's own additions" table with an explicit "no" so this decision is auditable rather than silently dropped.
6. **Independent verification I performed beyond what the skill's mechanism requires.** Neither `SKILL.md` nor `verify.md` asks the reviewer (as opposed to the verifier) to re-check the verifier's confirmations. I did so anyway, on 5 of the 9, because the skill's whole design point — recall-first finding with a mandatory fresh-context check — is exactly the kind of claim a holdout evaluation of this skill would want independently corroborated where cheap to do, and it cost a handful of `grep`/`diff` calls against material I already had open. This is not part of the skill's own contract; I did it as due diligence within my own role as "the reviewer" (dispatch: "You are the reviewer for this cell... Do the review yourself"), and I disclose it as exactly that — a judgment call to go beyond the letter of the pipeline, not something the pipeline itself demanded.
7. **Coverage classification: `complete`.** Both finders marked every one of the 10 changed files `reviewed` (none `ignored`), with no file left unfinished and no fetch or check abandoned by either finder or by me. `publishing.md`'s bar ("every file in the changed-file manifest is `reviewed` or `ignored` with a defensible reason, and every fetch and check the run started either finished or is named as unfinished") is met.
8. **Re-dispatching finders for shape-only fixes, not full re-investigation.** `SKILL.md` step 2 is explicit that a shape-violating finder gets "re-dispatch[ed]... once with its original prompt plus the violation lines and the instruction to return the same review in conforming shape; do not re-run the investigation." I implemented this as a fresh `Agent` call (not a session continuation) carrying the finder's own prior report verbatim, the exact violation lines from `validate_finder_report.py`'s stdout, and an explicit instruction not to re-investigate — both finders' re-dispatch responses changed only the flagged rows (confirmed by diffing the before/after ledger blocks myself) and nothing else, including the Requirements finder reading two named upstream files only to find real line numbers for two rows, which I judge within the letter of "do not re-run the investigation" since it added no new claim, candidate, or judgment — only a citation's precision.

**Wall clock:** not tracked by wall-clock timestamps on my side (the harness does not surface them to me mid-run); the sub-agent transcripts each report their own `duration_ms` (§ 1's token-usage line): 323s + 37s (Code finder + its shape-fix) + 892s + 61s (Requirements finder + its shape-fix) + 305s (verifier) = approximately 1,618 seconds (~27 minutes) of sub-agent wall-clock time, run strictly sequentially per the dispatch's foreground requirement, plus my own reading, scripting, cross-checking, and writing time around and between those five dispatches, which the harness does not report a figure for.
