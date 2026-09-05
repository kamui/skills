# Review payload — `python/typeshed#9458` (Panel line, seed 2)

*This file renders the review exactly as it would have been submitted in one `gh api ... pulls/9458/reviews` call: the summary as the review body, each finding below as its line comment. Publication is disabled for this cell; nothing here was posted anywhere.*

## Summary (review body)

**Mode: retrospective review of an already-merged pull request.** `python/typeshed#9458` ("Bump redis to 4.4.0") merged 2023-01-05T15:25:11Z. Publication is disabled for this run; this document renders the review exactly as it would have been posted, and stops there. Posting identity `kamui` did not author the pull request — an ordinary first review by a third party, event `COMMENT`.

**Changes Requested (advisory)** — 7 blocking findings, 1 optional finding, 0 open questions.

Code: Findings — 1 confirmed (`can_read`/`can_read_destructive`), merged into the Requirements finding of the same defect per the dedup rule that keeps the Requirements framing; no separately Code-tagged finding is published below. Requirements: Findings — 7 blocking, 1 optional; issue alignment: available (originating reference [`python/typeshed#9329`](https://github.com/python/typeshed/pull/9329), a closed, unmerged pull request the reviewed PR closes via `Closes #9329`, treated as the spec source).

Reviewed `55dfb4511` against `main` (merge-base `8365b1aa`). Coverage: complete — all 10 changed files were marked `reviewed` by both finders, and neither finder named an unfinished check. Disclosure: the Requirements finder's disposition ledger failed the mechanical shape validator (`scripts/validate_finder_report.py`) twice, on one non-`candidate` (`observation`) row's evidence field — see the research report §5.4 for the exact violation. This does not touch any published finding (the offending row is not a candidate, and the verifier-prompt builder never reads that row's evidence field), and it does not change this review's status, because an unsettled `must-fix` already resolves the status derivation at ladder step 1, before the coverage step that the skill's own two-failure rule would otherwise force to `Incomplete`. Disclosed per that rule rather than left silent.

This PR faithfully carries forward every signature change redis-py 4.4.0 made to members the stub already declared, but never swept the release for what it *added*: a renamed async read-readiness method, a new version-bump-time function, several new public methods and a new exception class, and two package-level re-export lists all still read as 4.3.5's surface after the bump lands. `can_read_destructive` is the one place this silently breaks working code — 4.4.0's own connection-pool internals call it — and the stub's `ExpiryT` alias is still typed as `float` even though passing a `float` to `set`/`setex` has always raised `redis.exceptions.DataError` at runtime in both releases; fix those two first, and treat the remaining five `must-fix` gaps as the same missing-completeness pattern recurring in isolation.

Findings (worst first):

- [Requirements] [must-fix] [P1] — `can_read_destructive` never added after `can_read` was retired — anchor [`stubs/redis/redis/asyncio/connection.pyi:61`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L61)
- [Requirements] [must-fix] [P1] — `ExpiryT` alias still `float | timedelta` after upstream narrowed it to `int | timedelta` — anchor [`stubs/redis/redis/commands/core.pyi:821`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi?plain=1#L821); fix [`stubs/redis/redis/typing.pyi:14`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/typing.pyi?plain=1#L14)
- [Requirements] [must-fix] [P2] — `get_retry`/`set_retry` accessors missing on `Redis`, `ConnectionPool`, `RedisCluster` — anchor [`stubs/redis/redis/cluster.pyi:66`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L66); fix [`stubs/redis/redis/cluster.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi)
- [Requirements] [must-fix] [P2] — `AbstractRedisCluster.replace_default_node` missing — anchor [`stubs/redis/redis/cluster.pyi:66`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L66); fix [`stubs/redis/redis/cluster.pyi:34`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L34)
- [Requirements] [must-fix] [P2] — `default_backoff()` function never stubbed — anchor [`stubs/redis/redis/backoff.pyi:28`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L28)
- [Requirements] [must-fix] [P2] — package `__init__.pyi` re-export lists not updated for new 4.4.0 names — anchor [`stubs/redis/redis/credentials.pyi:3`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/credentials.pyi?plain=1#L3); fix [`stubs/redis/redis/__init__.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi)
- [Requirements] [must-fix] [P2] — `MaxConnectionsError` exception class missing — anchor [`stubs/redis/redis/cluster.pyi:66`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L66); fix [`stubs/redis/redis/exceptions.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/exceptions.pyi)
- [Requirements] [consider] [P3] — `bitfield_ro` command method missing — anchor [`stubs/redis/METADATA.toml:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/METADATA.toml?plain=1#L1); fix [`stubs/redis/redis/commands/core.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi)

## Observations

These are accurate observations, not findings — no action is requested.

- The stub package has no `stubs/redis/redis/asyncio/cluster.pyi` at all, though upstream's `redis/asyncio/cluster.py` module predates 4.3.5 and grew further in 4.4.0 (`stubs/redis/redis/asyncio/cluster.pyi`).
- `stubs/redis/redis/exceptions.pyi` is not touched anywhere in this diff (`stubs/redis/redis/exceptions.pyi`).
- `stubs/redis/redis/asyncio/sentinel.pyi:18`'s new `# type: ignore[override]` comment is explained by, not a defect of, the widened `Connection.read_response` signature this same diff makes (`stubs/redis/redis/asyncio/sentinel.pyi:18`).

*(No observations were dropped at the cap — exactly 3 survived deduplication, at the limit.)*

## Open questions

None. The verifier returned zero `plausible` verdicts.

## Disputed

None. This is a first review; nothing has been replied to or re-verdicted yet.

<!-- review-run workflow=v2a-1 head=55dfb451101480275ae05f2f08d1a899a691a77d base-ref=main base-sha=8365b1aaefd46d506ca0dfe73e9721da2d03c566 merge-base=8365b1aaefd46d506ca0dfe73e9721da2d03c566 issues=python/typeshed#9329 coverage=incomplete -->

---

## Line comments (rendered as they would attach to the diff)

**[Requirements] [must-fix] [P1] `can_read_destructive` never added after `can_read` was retired**

`stubs/redis/redis/asyncio/connection.pyi:61` — upstream redis-py 4.4.0 replaces `can_read` with `async def can_read_destructive(self) -> bool` on `BaseParser`, `PythonParser`, and `HiredisParser`, and with `async def can_read_destructive(self)` on `Connection`. This diff correctly deletes the retired `can_read` from all four stub classes but never adds `can_read_destructive` to any of them — `grep -rn "can_read_destructive" stubs/redis/` finds nothing.

**Triggers when**: any typed async caller — including code modeling redis-py's own internal `ConnectionPool.get_connection`, which calls `await connection.can_read_destructive()` twice to detect a dirty pooled connection before reuse — is rejected by a type checker with an unknown-attribute error, even though the method is the real, public, no-underscore runtime API for redis-py 4.4.0, the version this stub package's `METADATA.toml` now claims to support.

**Change**: add `async def can_read_destructive(self) -> bool: ...` to `BaseParser`, `PythonParser`, and `HiredisParser`, and `async def can_read_destructive(self): ...` to `Connection`, in `stubs/redis/redis/asyncio/connection.pyi`, replacing the deleted `can_read` at each site.

<!-- finding id=requirements/asyncio-connection-pyi/missing-can-read-destructive axis=requirements action=must-fix priority=P1 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P1] `ExpiryT` alias still `float | timedelta` after upstream narrowed it to `int | timedelta`**

`stubs/redis/redis/commands/core.pyi:821` — redis-py 4.4.0 changed `redis/typing.py`'s `ExpiryT = Union[float, timedelta]` to `Union[int, timedelta]`. `stubs/redis/redis/typing.pyi:14` still reads `ExpiryT: TypeAlias = float | timedelta`, and the same union is inlined again (not via the alias) at `stubs/redis/redis/commands/core.pyi:359-360` and `:463-464` for the `ex`/`px` parameters. This diff fixes the sibling `StreamIdT` alias usage in the very same file but leaves `ExpiryT` untouched everywhere. The gap is not merely documentary: `BasicKeyCommands.set`/`setex` have raised a real runtime `redis.exceptions.DataError` for a non-`int` `ex`/`px` in both 4.3.5 and 4.4.0 (`redis/commands/core.py`, `"ex must be datetime.timedelta or int"`), so the stub has never correctly modeled this method's accepted types — 4.4.0's own corrected type hint was the opportunity this diff should have used to fix it.

**Triggers when**: code passing a `float` — e.g. `client.set(key, value, ex=1.5)` or `client.setex(key, 1.5, value)` — type-checks as valid against the stub but raises `DataError` at runtime, in both the pre- and post-bump library versions.

**Change**: change `stubs/redis/redis/typing.pyi:14` to `ExpiryT: TypeAlias = int | timedelta`, and update the inlined `ex`/`px` unions at `stubs/redis/redis/commands/core.pyi:359-360,463-464` to `int | timedelta` (or reference `ExpiryT` directly).

<!-- finding id=requirements/typing-pyi/stale-expiryt-alias axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/typing.pyi:14 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P2] `get_retry`/`set_retry` accessors missing on `Redis`, `ConnectionPool`, `RedisCluster`**

`stubs/redis/redis/cluster.pyi:66` — redis-py 4.4.0 adds `get_retry()`/`set_retry(retry)` to `redis.client.Redis` (sync and async) and `redis.cluster.RedisCluster`, and `set_retry(retry)` to `redis.connection.ConnectionPool` (sync and async). This diff wires the new `retry: Retry | None` constructor parameter into `RedisCluster.__init__` but adds none of the five accessor methods anywhere in the stub tree (`grep -rn "get_retry\|set_retry" stubs/redis/redis/` finds nothing).

**Triggers when**: a typed caller does `client.get_retry()` or `client.set_retry(my_retry)` on a `Redis`, `RedisCluster`, or (for `set_retry` only) `ConnectionPool` instance — documented runtime usage for swapping retry policy — and a type checker reports it as an unknown attribute.

**Change**: add `def get_retry(self) -> Retry | None: ...` and `def set_retry(self, retry: Retry) -> None: ...` to `Redis` in `stubs/redis/redis/client.pyi` and `stubs/redis/redis/asyncio/client.pyi`; add `def set_retry(self, retry: Retry) -> None: ...` to `ConnectionPool` in `stubs/redis/redis/connection.pyi` and `stubs/redis/redis/asyncio/connection.pyi`; add both methods to `RedisCluster` in `stubs/redis/redis/cluster.pyi`.

<!-- finding id=requirements/retry-accessors/missing-get-set-retry axis=requirements action=must-fix priority=P2 fix=stubs/redis/redis/cluster.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P2] `AbstractRedisCluster.replace_default_node` missing**

`stubs/redis/redis/cluster.pyi:66` — redis-py 4.4.0 adds a new public method, `AbstractRedisCluster.replace_default_node(self, target_node=None) -> None`, for moving the cluster's default node after a topology change. `stubs/redis/redis/cluster.pyi`'s `AbstractRedisCluster` class has no `replace_default_node` entry, though this same diff touches `cluster.pyi` for the sibling `retry` parameter and the `__nonzero__` removal.

**Triggers when**: a caller invokes `cluster_client.replace_default_node()` and a type checker reports it as an unknown attribute, even though it is the documented, real 4.4.0 API.

**Change**: add `def replace_default_node(self, target_node: ClusterNode | None = ...) -> None: ...` to `AbstractRedisCluster` in `stubs/redis/redis/cluster.pyi`.

<!-- finding id=requirements/cluster-pyi/missing-replace-default-node axis=requirements action=must-fix priority=P2 fix=stubs/redis/redis/cluster.pyi:34 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P2] `default_backoff()` function never stubbed**

`stubs/redis/redis/backoff.pyi:28` — redis-py 4.4.0 adds a module-level `def default_backoff(): return EqualJitterBackoff()` to `redis/backoff.py`, used internally by `RedisCluster.__init__` and re-exported from both `redis/__init__.py` and `redis/asyncio/__init__.py`. This diff updates every `*Backoff.__init__` signature in `stubs/redis/redis/backoff.pyi` to sync the new optional-argument defaults but adds no `default_backoff` stub anywhere (`grep -rn default_backoff stubs/redis/` finds nothing).

**Triggers when**: `import redis; redis.default_backoff()` — valid, documented top-level usage per the new `__all__` entry — is rejected by a type checker as an unknown name.

**Change**: add `def default_backoff() -> EqualJitterBackoff: ...` to `stubs/redis/redis/backoff.pyi`.

<!-- finding id=requirements/backoff-pyi/missing-default-backoff axis=requirements action=must-fix priority=P2 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P2] Package `__init__.pyi` re-export lists not updated for new 4.4.0 names**

`stubs/redis/redis/credentials.pyi:3` — redis-py 4.4.0's `redis/__init__.py` adds `CredentialProvider`, `UsernamePasswordCredentialProvider`, and `default_backoff` to its imports and `__all__`; `redis/asyncio/__init__.py` adds `RedisCluster`, `CommandsParser`, and `default_backoff` to its own. `stubs/redis/redis/__init__.pyi` and `stubs/redis/redis/asyncio/__init__.pyi` still carry the byte-identical 4.3.5 `__all__` lists — neither file is touched by this diff, even though this same diff adds `credentials.pyi`, defining the two credential classes upstream now re-exports from the top level.

**Triggers when**: `import redis; redis.CredentialProvider`, `redis.UsernamePasswordCredentialProvider`, or `redis.default_backoff` — all legitimate, `__all__`-documented top-level usages in 4.4.0 — are rejected by a type checker as unknown names (and likewise `redis.asyncio.CommandsParser` / `redis.asyncio.default_backoff`).

**Change**: add `from .credentials import CredentialProvider as CredentialProvider, UsernamePasswordCredentialProvider as UsernamePasswordCredentialProvider` and `from .backoff import default_backoff as default_backoff` (plus matching `__all__` entries) to `stubs/redis/redis/__init__.pyi`; add `from .parser import CommandsParser as CommandsParser` and `from redis.backoff import default_backoff as default_backoff` (plus `__all__` entries) to `stubs/redis/redis/asyncio/__init__.pyi`. `RedisCluster`'s async re-export additionally needs the still-missing `redis/asyncio/cluster.pyi` module authored first (see Observations).

<!-- finding id=requirements/package-init/stale-reexport-lists axis=requirements action=must-fix priority=P2 fix=stubs/redis/redis/__init__.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [must-fix] [P2] `MaxConnectionsError` exception class missing**

`stubs/redis/redis/cluster.pyi:66` — redis-py 4.4.0 adds `class MaxConnectionsError(ConnectionError)` to `redis/exceptions.py`, actively raised by the new `max_connections`-limiting behavior in `redis/asyncio/cluster.py`. `stubs/redis/redis/exceptions.pyi` has no `MaxConnectionsError` entry, and the file is not touched anywhere by this diff.

**Triggers when**: typed code does `except redis.exceptions.MaxConnectionsError:` around a pool-exhaustion scenario, and a type checker rejects it as an unknown attribute.

**Change**: add `class MaxConnectionsError(ConnectionError): ...` to `stubs/redis/redis/exceptions.pyi`.

<!-- finding id=requirements/exceptions-pyi/missing-maxconnectionserror axis=requirements action=must-fix priority=P2 fix=stubs/redis/redis/exceptions.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

---

**[Requirements] [consider] [P3] `bitfield_ro` command method missing**

`stubs/redis/METADATA.toml:1` — redis-py 4.4.0 adds `bitfield_ro(self, key, encoding, offset, default_overflow=None)` to `BasicKeyCommands`/`AsyncBasicKeyCommands`. `stubs/redis/redis/commands/core.pyi` defines `bitfield` (sync and async) but not `bitfield_ro`. No diff-touched line names this gap directly, so it is anchored at the version-bump line per the anchor ladder's fourth rung.

**Triggers when**: `client.bitfield_ro(...)` — the real, documented `BITFIELD_RO` Redis command added in this release — is rejected by a type checker as unknown.

**Change**: add `def bitfield_ro(self, key, encoding, offset, default_overflow: Any | None = ...): ...` (sync and async) to `stubs/redis/redis/commands/core.pyi`.

Closing this without action is a correct response.

<!-- finding id=requirements/commands-core-pyi/missing-bitfield-ro axis=requirements action=consider priority=P3 fix=stubs/redis/redis/commands/core.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->
