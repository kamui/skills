**Mode: retrospective review of a merged pull request.** `python/typeshed#9458` merged 2023-01-05T15:25:11Z. This review is posted by `kamui`, a third party who did not author the pull request. Publication is disabled for this run; what follows is rendered exactly as it would be submitted (`event=COMMENT`, one review call, one summary body plus separate line comments), and nothing was actually posted anywhere.

---

## Review body

**Changes Requested (advisory)** — 3 blocking findings, 1 open question.

Code: Passed — its one candidate (a missing `can_read_destructive` method) was confirmed but, per the verifier's deduplication rule, merged into the matching Requirements finding below, which carries the issue citation; no standalone Code-axis finding survives. Requirements: Findings — 3 blocking, 5 optional; 12 of 21 restated requirements met, 8 not met, 1 unverifiable; issue alignment: available (`python/typeshed#9329`).

Reviewed `55dfb4511` against `main` (merge-base `8365b1aa`). Coverage: complete — all 10 changed files inspected and marked `reviewed` by both finders; no fetch or check was abandoned.

This diff gets the mechanical parts of the 4.3.5→4.4.0 bump right — every touched line checks out against the real upstream signatures — but leaves five separate upstream 4.4.0 interface additions half-wired or entirely unaddressed. The three blocking findings share one shape: the diff adds *some* piece of an upstream change (a class, a parameter, a value) but not the sibling name that makes it reachable — most visibly, `from redis import CredentialProvider` (this PR's own headline feature) and `connection.can_read_destructive()` (a method upstream's own connection-pool code calls) are both now unreachable through the stub. The open question is about the review's own source material, not the code: two of the packet's authorized offline sources disagree about whether six further submodules changed at all.

- [Requirements] [must-fix] [P1] — top-level `redis/__init__.pyi` and `asyncio/__init__.pyi` miss the new 4.4.0 re-exports (`CredentialProvider`, `UsernamePasswordCredentialProvider`, `default_backoff`) — anchor [`stubs/redis/redis/credentials.pyi:3`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/credentials.pyi?plain=1#L3); fix [`stubs/redis/redis/__init__.pyi:4`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi?plain=1#L4)
- [Requirements] [must-fix] [P1] — `Redis`/`ConnectionPool`/`RedisCluster` miss the new `get_retry`/`set_retry`/`replace_default_node` — no honest anchor (spans 5 files); fix [`stubs/redis/redis/client.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/client.pyi) and 4 sibling classes, listed in full below
- [Requirements] [must-fix] [P1] — async `connection.pyi` never gained `can_read`'s 4.4.0 replacement, `can_read_destructive` — anchor [`stubs/redis/redis/asyncio/connection.pyi:135`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L135); fix [`stubs/redis/redis/asyncio/connection.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi) (four class sites)
- [Requirements] [consider] [P2] — `backoff.pyi` misses the new `DEFAULT_CAP`, `DEFAULT_BASE`, `default_backoff()` — anchor [`stubs/redis/redis/backoff.pyi:16`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L16); fix [`stubs/redis/redis/backoff.pyi:29`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L29)
- [Requirements] [consider] [P2] — `commands/core.pyi` misses the new `bitfield_ro` command — no honest anchor; fix [`stubs/redis/redis/commands/core.pyi:290`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi?plain=1#L290)
- [Requirements] [consider] [P2] — `exceptions.pyi` misses the new `MaxConnectionsError` class — no honest anchor; fix [`stubs/redis/redis/exceptions.pyi:42`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/exceptions.pyi?plain=1#L42)
- [Requirements] [consider] [P2] — `typing.pyi`'s `ExpiryT` still `float | timedelta`, not narrowed to `int | timedelta` — no honest anchor; fix [`stubs/redis/redis/typing.pyi:14`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/typing.pyi?plain=1#L14)
- [Requirements] [consider] [P3] — async `PubSub.get_message`'s `timeout` not widened to `float | None` — no honest anchor; fix [`stubs/redis/redis/asyncio/client.pyi:161`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/client.pyi?plain=1#L161)

Counts — Requirements axis: 3 must-fix, 5 consider (8 findings); 0 refuted (dropped, not shown); 1 question. Code axis: 0 standalone findings (1 candidate confirmed and merged into the Requirements list above).

### [Requirements] [must-fix] [P1] `redis/__init__.pyi` and `asyncio/__init__.pyi` miss the new 4.4.0 re-exports

[`stubs/redis/redis/credentials.pyi:3`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/credentials.pyi?plain=1#L3) — this diff adds `CredentialProvider`/`UsernamePasswordCredentialProvider` here, and upstream 4.4.0 adds them (plus `default_backoff`) to `redis/__init__.py`'s `__all__`, and `default_backoff` to `redis/asyncio/__init__.py`'s. Neither `stubs/redis/redis/__init__.pyi` nor `stubs/redis/redis/asyncio/__init__.pyi` was touched by this PR, and neither name appears in either file.

**Triggers when**: `from redis import CredentialProvider` or `from redis import default_backoff` — both valid at runtime and both part of this PR's own feature set — is rejected by a type checker.

**Change**: in [`stubs/redis/redis/__init__.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi), import `CredentialProvider`/`UsernamePasswordCredentialProvider` from `.credentials` and `default_backoff` from `.backoff`, and add all three to `__all__` following the file's existing re-export idiom; in [`stubs/redis/redis/asyncio/__init__.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/__init__.pyi), add `default_backoff` the same way (this needs the finding below fixed first, since `default_backoff` does not exist in `backoff.pyi` yet).

<!-- finding id=requirements/redis-init-reexports axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/__init__.pyi:4 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [must-fix] [P1] `Redis`/`ConnectionPool`/`RedisCluster` miss the new `get_retry`/`set_retry`/`replace_default_node`

Upstream 4.4.0 adds `Redis.get_retry()`/`set_retry()` to [`redis/client.py`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/client.pyi) and [`redis/asyncio/client.py`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/client.pyi), `ConnectionPool.set_retry()` to [`redis/connection.py`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/connection.pyi) and [`redis/asyncio/connection.py`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi), and `RedisCluster.get_retry()`/`set_retry()`/`replace_default_node()` to [`redis/cluster.py`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi) — all confirmed absent in the 4.3.5 upstream tree and present in 4.4.0. None of these five stub locations gained the corresponding methods; none of this PR's diff touches any of them. This finding has no single honest line anchor (finding-format.md's anchor ladder, rule 4): the gap spans five files and no diff line "opens" or "demonstrates" it, so it is carried in the body only, with no line comment.

**Triggers when**: `redis_client.get_retry()`, `pool.set_retry(new_retry)`, or `cluster.replace_default_node(node)` — all valid at runtime — is rejected by a type checker with "has no attribute".

**Change**: add `def get_retry(self) -> Retry | None: ...` / `def set_retry(self, retry: Retry) -> None: ...` to `Redis` in `client.pyi` and `asyncio/client.pyi`; `def set_retry(self, retry: Retry) -> None: ...` to `ConnectionPool` in `connection.pyi` and `asyncio/connection.pyi`; and `get_retry`/`set_retry`/`def replace_default_node(self, target_node: ClusterNode | None = ...) -> None: ...` to `RedisCluster` in `cluster.pyi`.

<!-- finding id=requirements/redis-retry-accessors axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/client.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [must-fix] [P1] async `connection.pyi` never gained `can_read`'s 4.4.0 replacement, `can_read_destructive`

[`stubs/redis/redis/asyncio/connection.pyi:135`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L135) — this line is where the diff folded `Connection`'s old `can_read`/`read_response` pair into the new `read_response(self, disable_decoding=..., timeout=...)`. Upstream 4.4.0 instead renames `can_read(timeout)` to `can_read_destructive()` (no `timeout` param) on `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `redis/asyncio/connection.py` — the diff correctly deletes every `can_read` stub line on all four classes but adds `can_read_destructive` nowhere. `ConnectionPool.get_connection` in the real library calls `await connection.can_read_destructive()` as normal operation, so this is not dead code.

**Triggers when**: `await connection.can_read_destructive()` (including inside `redis-py`'s own `ConnectionPool.get_connection`), or a parser's `can_read_destructive()`, is rejected by a type checker as an unknown attribute, even though it is valid, documented runtime behavior.

**Change**: add `async def can_read_destructive(self) -> bool: ...` to `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in [`stubs/redis/redis/asyncio/connection.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi), at the four sites where `can_read` was removed.

<!-- finding id=requirements/asyncio-can-read-destructive axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/asyncio/connection.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [consider] [P2] `backoff.pyi` misses the new `DEFAULT_CAP`, `DEFAULT_BASE`, `default_backoff()`

[`stubs/redis/redis/backoff.pyi:16`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L16) — this line is one of the four places this diff gives `cap`/`base` a default value on the `*Backoff` subclasses, sourced from upstream's new module-level `DEFAULT_CAP = 0.512` / `DEFAULT_BASE = 0.008` constants and its new `default_backoff()` factory (confirmed absent in 4.3.5, present in 4.4.0). None of the three new names is declared anywhere in `backoff.pyi`.

**Triggers when**: `from redis.backoff import default_backoff` or `redis.backoff.DEFAULT_CAP` — both valid at runtime — is rejected by a type checker.

**Change**: append `DEFAULT_CAP: float`, `DEFAULT_BASE: float`, and `def default_backoff() -> EqualJitterBackoff: ...` to [`stubs/redis/redis/backoff.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L29).

Closing this without action is a correct response.

<!-- finding id=requirements/backoff-default-backoff axis=requirements action=consider priority=P2 fix=stubs/redis/redis/backoff.pyi:29 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [consider] [P2] `commands/core.pyi` misses the new `bitfield_ro` command

Upstream 4.4.0 adds `def bitfield_ro(self, key, encoding, offset, items=None) -> ResponseT` to the shared `BasicKeyCommands` mixin in `redis/commands/core.py` (confirmed absent in 4.3.5). This PR's diff touches [`stubs/redis/redis/commands/core.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi) for an unrelated `xautoclaim` typing fix, but `bitfield_ro` is absent from both the sync and async mixin classes. No diff line in this file relates topically to `bitfield_ro`, so this finding has no honest line anchor and is carried in the body only.

**Triggers when**: `redis_client.bitfield_ro(key, "u8", "#0")` — a valid new 4.4.0 command — is rejected by a type checker.

**Change**: add `def bitfield_ro(self, key: KeyT, encoding: str, offset: BitfieldOffsetT, items: list[Any] | None = ...) -> ResponseT: ...` (and its `Awaitable`-returning async counterpart) to [`stubs/redis/redis/commands/core.pyi:290`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi?plain=1#L290), next to `bitfield`.

Closing this without action is a correct response.

<!-- finding id=requirements/bitfield-ro axis=requirements action=consider priority=P2 fix=stubs/redis/redis/commands/core.pyi:290 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [consider] [P2] `exceptions.pyi` misses the new `MaxConnectionsError` class

Upstream 4.4.0 adds `class MaxConnectionsError(ConnectionError): ...` to `redis/exceptions.py` — the only change to that file between the two tags. `stubs/redis/redis/exceptions.pyi` was not touched by this PR and none of its 20 exception classes is `MaxConnectionsError`. No file in this PR's diff relates topically to exceptions, so this finding has no honest line anchor and is carried in the body only.

**Triggers when**: `except redis.exceptions.MaxConnectionsError:` — valid, and raised by upstream on connection-pool exhaustion — is rejected by a type checker ("has no attribute").

**Change**: add `class MaxConnectionsError(ConnectionError): ...` to [`stubs/redis/redis/exceptions.pyi:42`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/exceptions.pyi?plain=1#L42), after the existing exception classes.

Closing this without action is a correct response.

<!-- finding id=requirements/max-connections-error axis=requirements action=consider priority=P2 fix=stubs/redis/redis/exceptions.pyi:42 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [consider] [P2] `typing.pyi`'s `ExpiryT` still `float | timedelta`, not narrowed to `int | timedelta`

Upstream 4.4.0 narrows `ExpiryT = Union[float, timedelta]` to `Union[int, timedelta]` in `redis/typing.py` — the only change to that file between the two tags. `stubs/redis/redis/typing.pyi` was not touched by this PR and still declares `ExpiryT: TypeAlias = float | timedelta`; `ExpiryT` is used by reference throughout `commands/core.pyi`'s `expire`/`setex`/`getex`-family signatures. No file in this PR's diff relates topically to `typing.pyi`, so this finding has no honest line anchor and is carried in the body only.

**Triggers when**: `redis_client.expire(key, 1.5)` — a `float`, which the stub still accepts via `ExpiryT` — no longer matches what upstream's own 4.4.0 type annotations declare acceptable, so a type checker gives no warning where upstream's own typing now intends one.

**Change**: change [`stubs/redis/redis/typing.pyi:14`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/typing.pyi?plain=1#L14) to `ExpiryT: TypeAlias = int | timedelta`.

Closing this without action is a correct response.

<!-- finding id=requirements/expiry-t-narrowing axis=requirements action=consider priority=P2 fix=stubs/redis/redis/typing.pyi:14 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### [Requirements] [consider] [P3] async `PubSub.get_message`'s `timeout` not widened to `float | None`

Upstream 4.4.0 changes async `PubSub.get_message`'s signature from `timeout: float = 0.0` to `timeout: Optional[float] = 0.0` in `redis/asyncio/client.py`, with a real behavior change (`block=(timeout is None)`; the docstring now documents `None` as "wait indefinitely"). `stubs/redis/redis/asyncio/client.pyi:161` still reads `timeout: float = ...`. `get_message` itself is not touched anywhere in this PR's diff, so this finding has no honest line anchor and is carried in the body only.

**Triggers when**: `await pubsub.get_message(timeout=None)` — upstream's documented way to wait indefinitely as of 4.4.0 — is rejected by a type checker.

**Change**: change [`stubs/redis/redis/asyncio/client.pyi:161`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/client.pyi?plain=1#L161)'s `timeout: float = ...` to `timeout: float | None = ...`.

Closing this without action is a correct response.

<!-- finding id=requirements/get-message-timeout-none axis=requirements action=consider priority=P3 fix=stubs/redis/redis/asyncio/client.pyi:161 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

## Observations

These are accurate observations, not findings — no action is requested.

- `CredentialProvider.get_credentials` is marked `@abstractmethod` even though `CredentialProvider` does not subclass `ABC` — the decorator has no enforcement effect without an ABC base (`stubs/redis/redis/credentials.pyi:4`).
- Async `Lock.redis` is still typed `Redis[Any]`, narrower than upstream 4.4.0's widened `Union["Redis", "RedisCluster"]`; a full fix is blocked by `redis.asyncio.cluster` having no stub at all in this package (`stubs/redis/redis/asyncio/lock.pyi:26`).
- The `# type: ignore[override]` this diff adds to `SentinelManagedConnection.read_response` silences, rather than resolves, the Liskov mismatch this same diff introduced by giving the base `Connection.read_response` a new `timeout` parameter (`stubs/redis/redis/asyncio/sentinel.pyi:18`).

## Open questions

**[Question] Did `redis.commands.{bf,graph,redismodules,search,timeseries}` actually change between v4.3.5 and v4.4.0?**

The issue's linked specification (the upstream `redis-py` v4.3.5→v4.4.0 compare) was supplied offline as two things: a GitHub compare `.diff` file, and two complete source trees at the two tags. They disagree. The `.diff` file shows real hunks for `redis/commands/bf/commands.py`, `redis/commands/graph/__init__.py`, `redis/commands/graph/commands.py`, `redis/commands/graph/query_result.py`, `redis/commands/redismodules.py`, `redis/commands/search/__init__.py`, and `redis/commands/timeseries/commands.py` (e.g. adding `TDIGEST_TRIMMED_MEAN`, `deprecated_function` to `bf/commands.py`). A direct byte comparison of the two provided tree snapshots shows all seven files are identical between the tags — and the "4.3.5" tree snapshot already contains `TDIGEST_TRIMMED_MEAN`/`deprecated_function`, contradicting the `.diff` file's claim that those were introduced only in this transition. No static reading of the code available in this review can settle which source is authoritative, so I cannot tell whether the stub's continued silence on `stubs/redis/redis/commands/{bf,graph,json,redismodules,search,timeseries}` (all untouched by this PR) is correct or a further gap.

**Change no code for this.** Regenerate or re-fetch a `.diff`/tree pair for these specific paths from the real `redis-py` history (e.g. `git diff v4.3.5...v4.4.0 -- redis/commands/{bf,graph,json,redismodules,search,timeseries}` against an authoritative clone) that agrees with itself, then re-run this sweep; if it turns out these submodules did change, treat any newly-revealed gap the same way as the findings above.

<!-- finding id=question/submodule-interface-parity-undecidable action=question head=55dfb451101480275ae05f2f08d1a899a691a77d -->

<!-- review-run workflow=v2a-1 head=55dfb451101480275ae05f2f08d1a899a691a77d base-ref=main base-sha=8365b1aaefd46d506ca0dfe73e9721da2d03c566 merge-base=8365b1aaefd46d506ca0dfe73e9721da2d03c566 issues=python/typeshed#9329 coverage=complete -->

---

## Line comments (would post as separate PR review comments, each anchored to its `path`/`line`)

Per `publishing.md` § One review, one call: findings with a genuine diff-touched line anchor go on that code as separate line comments; the body above carries only their index entry. The three findings below are exactly the text of those comments — identical to their body-section text above, reproduced here to show what would physically attach to `stubs/redis/redis/credentials.pyi:3`, `stubs/redis/redis/asyncio/connection.pyi:135`, and `stubs/redis/redis/backoff.pyi:16` respectively (`side: RIGHT` on all three; this run posted none of it, since publication is disabled).

### Line comment 1 — `path: stubs/redis/redis/credentials.pyi`, `line: 3`, `side: RIGHT`

**[Requirements] [must-fix] [P1] `redis/__init__.pyi` and `asyncio/__init__.pyi` miss the new 4.4.0 re-exports**

`stubs/redis/redis/credentials.pyi:3` — this diff adds `CredentialProvider`/`UsernamePasswordCredentialProvider` here, and upstream 4.4.0 adds them (plus `default_backoff`) to `redis/__init__.py`'s `__all__`, and `default_backoff` to `redis/asyncio/__init__.py`'s. Neither `stubs/redis/redis/__init__.pyi` nor `stubs/redis/redis/asyncio/__init__.pyi` was touched by this PR, and neither name appears in either file.

**Triggers when**: `from redis import CredentialProvider` or `from redis import default_backoff` — both valid at runtime and both part of this PR's own feature set — is rejected by a type checker.

**Change**: in `stubs/redis/redis/__init__.pyi`, import `CredentialProvider`/`UsernamePasswordCredentialProvider` from `.credentials` and `default_backoff` from `.backoff`, and add all three to `__all__` following the file's existing re-export idiom; in `stubs/redis/redis/asyncio/__init__.pyi`, add `default_backoff` the same way (needs the `backoff.pyi` finding fixed first).

<!-- finding id=requirements/redis-init-reexports axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/__init__.pyi:4 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### Line comment 2 — `path: stubs/redis/redis/asyncio/connection.pyi`, `line: 135`, `side: RIGHT`

**[Requirements] [must-fix] [P1] async `connection.pyi` never gained `can_read`'s 4.4.0 replacement, `can_read_destructive`**

`stubs/redis/redis/asyncio/connection.pyi:135` — this line is where the diff folded `Connection`'s old `can_read`/`read_response` pair into the new `read_response(self, disable_decoding=..., timeout=...)`. Upstream 4.4.0 instead renames `can_read(timeout)` to `can_read_destructive()` (no `timeout` param) on `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `redis/asyncio/connection.py` — the diff correctly deletes every `can_read` stub line on all four classes but adds `can_read_destructive` nowhere. `ConnectionPool.get_connection` in the real library calls `await connection.can_read_destructive()` as normal operation, so this is not dead code.

**Triggers when**: `await connection.can_read_destructive()` (including inside `redis-py`'s own `ConnectionPool.get_connection`), or a parser's `can_read_destructive()`, is rejected by a type checker as an unknown attribute, even though it is valid, documented runtime behavior.

**Change**: add `async def can_read_destructive(self) -> bool: ...` to `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `stubs/redis/redis/asyncio/connection.pyi`, at the four sites where `can_read` was removed.

<!-- finding id=requirements/asyncio-can-read-destructive axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/asyncio/connection.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### Line comment 3 — `path: stubs/redis/redis/backoff.pyi`, `line: 16`, `side: RIGHT`

**[Requirements] [consider] [P2] `backoff.pyi` misses the new `DEFAULT_CAP`, `DEFAULT_BASE`, `default_backoff()`**

`stubs/redis/redis/backoff.pyi:16` — this line is one of the four places this diff gives `cap`/`base` a default value on the `*Backoff` subclasses, sourced from upstream's new module-level `DEFAULT_CAP = 0.512` / `DEFAULT_BASE = 0.008` constants and its new `default_backoff()` factory (confirmed absent in 4.3.5, present in 4.4.0). None of the three new names is declared anywhere in `backoff.pyi`.

**Triggers when**: `from redis.backoff import default_backoff` or `redis.backoff.DEFAULT_CAP` — both valid at runtime — is rejected by a type checker.

**Change**: append `DEFAULT_CAP: float`, `DEFAULT_BASE: float`, and `def default_backoff() -> EqualJitterBackoff: ...` to `stubs/redis/redis/backoff.pyi:29`.

Closing this without action is a correct response.

<!-- finding id=requirements/backoff-default-backoff axis=requirements action=consider priority=P2 fix=stubs/redis/redis/backoff.pyi:29 head=55dfb451101480275ae05f2f08d1a899a691a77d -->
