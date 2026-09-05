# Review payload — python/typeshed#9458 (retrospective, non-publishing)

Event: `COMMENT` (advisory; publication disabled per retrospective-merged-target rule). Posting identity: `kamui`.

## Summary body

**Changes Requested (advisory)** — 5 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Bump the `redis` stubs from 4.3.5 to 4.4.0, tracking the corresponding upstream `redis-py` release (closes #9329, a stubsabot bump PR whose body links the `v4.3.5...v4.4.0` compare diff as its spec): a new `credentials` module, `credential_provider` constructor parameters, an async parser/connection API rename, a `RedisCluster` `retry` parameter, a `lock()` `blocking` parameter, and an `xautoclaim` `StreamIdT` type.

**Issue fit:** Partial — every API change this diff does implement matches the upstream 4.4.0 source exactly (verified against the pinned `redis-py` 4.3.5 and 4.4.0 trees). Several sibling pieces of the same upstream changes are missing: the async parser/connection rename drops `can_read` without adding its 4.4.0 replacement `can_read_destructive`; the new `credentials` module is stubbed but never re-exported from `redis/__init__.pyi` even though the runtime's `__all__` now includes it; the new `credential_provider` constructor argument isn't declared as a `Connection` instance attribute; and the new `RedisCluster`, `Redis`, and `ConnectionPool` retry-accessor methods (`get_retry`/`set_retry`) added throughout `redis-py` 4.4.0 have no stub coverage at all.

**Coverage:** Complete merge-base diff reviewed (10 files, +41/−36); every changed file inspected via the function-context diff and, where the change added or removed a class member, the containing class's full attribute/method list. Cross-checked against the pinned `redis-py` 4.3.5 and 4.4.0 source trees (the issue's linked spec) for every added, removed, or renamed member. `CONTRIBUTING.md` read for stub-completeness and typing conventions. No test or generated-artifact files changed. All five candidates proposed `must-fix` were independently verified in a fresh context; all five were confirmed.

**Reviewed:** `55dfb4511` against merge-base `8365b1a`.

## Findings

- [P2] [must-fix] Restore async `can_read_destructive` after the `can_read` rename — anchor `stubs/redis/redis/asyncio/connection.pyi:49`; fix [`stubs/redis/redis/asyncio/connection.pyi:74`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L74)
- [P3] [must-fix] Declare `Connection.credential_provider` as an instance attribute — anchor [`stubs/redis/redis/asyncio/connection.pyi:120`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L120); fix [`stubs/redis/redis/asyncio/connection.pyi:94`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi?plain=1#L94)
- [P2] [must-fix] Add the `retry` attribute and `get_retry`/`set_retry` to `RedisCluster` — anchor [`stubs/redis/redis/cluster.pyi:66`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L66); fix [`stubs/redis/redis/cluster.pyi:59`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L59)

## Unanchored findings

- **[P2] [must-fix] Export `CredentialProvider` from `redis/__init__.pyi`**

  **Triggers when:** Code does `from redis import CredentialProvider` or `from redis import UsernamePasswordCredentialProvider`.

  **Impact:** redis-py 4.4.0 added both names to `redis/__init__.py`'s `__all__`. This diff adds the new `redis/credentials.pyi` module but never re-exports either name from `redis/__init__.pyi`, so the top-level import the runtime advertises is rejected as unresolved by a type checker.

  **Change:** In `stubs/redis/redis/__init__.pyi`, re-export both names (e.g. `from .credentials import CredentialProvider as CredentialProvider, UsernamePasswordCredentialProvider as UsernamePasswordCredentialProvider`) and add them to `__all__`.

  **Source:** Issue python/typeshed#9329, the redis-py 4.3.5...4.4.0 diff it links; `CONTRIBUTING.md`, "What to include".

  anchor [`stubs/redis/redis/__init__.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi) (file); fix [`stubs/redis/redis/__init__.pyi:2`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi?plain=1#L2)

- **[P3] [must-fix] Add the new 4.4.0 `get_retry`/`set_retry` accessors to `Redis` and `ConnectionPool`**

  **Triggers when:** Code calls `redis_client.get_retry()`, `redis_client.set_retry(r)`, or `pool.set_retry(r)` on the sync or async client/connection-pool classes.

  **Impact:** redis-py 4.4.0 adds `Redis.get_retry`/`set_retry` (sync and async) and `ConnectionPool.set_retry` (sync and async) — five new public methods — but none appear in `stubs/redis/redis/client.pyi`, `asyncio/client.pyi`, `connection.pyi`, or `asyncio/connection.pyi`, each of which this diff otherwise edits.

  **Change:** Add `def get_retry(self) -> Retry | None: ...` and `def set_retry(self, retry: Retry) -> None: ...` to `Redis` in `client.pyi` and `asyncio/client.pyi`; add `def set_retry(self, retry: Retry) -> None: ...` to `ConnectionPool` in `connection.pyi` and `asyncio/connection.pyi`.

  **Source:** Issue python/typeshed#9329, the redis-py 4.3.5...4.4.0 diff it links.

  anchor [`stubs/redis/redis/asyncio/client.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/client.pyi) (file); fix [`stubs/redis/redis/client.pyi:274`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/client.pyi?plain=1#L274)

<!-- review-run head=55dfb451101480275ae05f2f08d1a899a691a77d base-ref=main base-sha=70025c372346288675437fc0bd273db84cc0b3d5 merge-base=8365b1aaefd46d506ca0dfe73e9721da2d03c566 workflow=v5b-1 context=62453b2c82386967adabff8652687099ad7a12ff8d74073279ef6818867eca33 issues=python/typeshed#9329 coverage=complete -->

## Inline review comments

### Comment on `stubs/redis/redis/asyncio/connection.pyi:49` (side LEFT)

**[P2] [must-fix] Restore async `can_read_destructive` after the `can_read` rename**

**Triggers when:** Type-checked code calls `can_read_destructive()` on an async `Connection`, `BaseParser`, `PythonParser`, or `HiredisParser` instance.

**Impact:** redis-py 4.4.0 renamed the async parser/connection method `can_read` to `can_read_destructive`. This diff removes `can_read` from all four classes but adds no replacement, so a public, working runtime method has zero stub coverage and any caller sees "has no attribute `can_read_destructive`".

**Change:** In `stubs/redis/redis/asyncio/connection.pyi`, add `async def can_read_destructive(self) -> bool: ...` to `BaseParser` and `PythonParser`, and `async def can_read_destructive(self): ...` to `HiredisParser` and `Connection`.

<!-- finding id=redis-asyncio-connection/can-read-destructive head=55dfb451101480275ae05f2f08d1a899a691a77d priority=P2 action=must-fix blocking=true kind=bug fix=stubs/redis/redis/asyncio/connection.pyi:74 -->

### Comment on `stubs/redis/redis/asyncio/connection.pyi:120` (side RIGHT)

**[P3] [must-fix] Declare `Connection.credential_provider` as an instance attribute**

**Triggers when:** Code reads `connection.credential_provider` after constructing a sync or async `Connection`.

**Impact:** Both `Connection.__init__` implementations store the new `credential_provider` argument as `self.credential_provider`, but neither stub's `Connection` class body lists it as an attribute, unlike every sibling `__init__` parameter. The same-named, valid runtime attribute access is flagged as undefined by a type checker.

**Change:** Add `credential_provider: CredentialProvider | None` to the `Connection` attribute list in both `stubs/redis/redis/asyncio/connection.pyi` (after `redis_connect_func`, line 94) and `stubs/redis/redis/connection.pyi` (after `redis_connect_func`, line 98).

<!-- finding id=redis-connection/credential-provider-attribute head=55dfb451101480275ae05f2f08d1a899a691a77d priority=P3 action=must-fix blocking=true kind=bug fix=stubs/redis/redis/asyncio/connection.pyi:94 -->

### Comment on `stubs/redis/redis/cluster.pyi:66` (side RIGHT)

**[P2] [must-fix] Add the `retry` attribute and `get_retry`/`set_retry` to `RedisCluster`**

**Triggers when:** Code reads `cluster.retry`, or calls `cluster.get_retry()` / `cluster.set_retry(r)`.

**Impact:** redis-py 4.4.0 adds `RedisCluster.get_retry`/`set_retry` and stores the constructor's `retry` argument as `self.retry` when one is passed. This diff adds the `retry` constructor parameter to the stub but none of the attribute or the two new accessor methods, leaving the rest of this same feature unstubbed. `self.retry` is set only when a `retry` argument is passed, not unconditionally, so `get_retry()` can also raise `AttributeError` despite its `Optional["Retry"]` return annotation — type the attribute `Retry | None`, not `Retry`.

**Change:** In `stubs/redis/redis/cluster.pyi`'s `RedisCluster`, add `retry: Retry | None` to the attribute list (line 59) and `def get_retry(self) -> Retry | None: ...` / `def set_retry(self, retry: Retry) -> None: ...` near `get_connection_kwargs` (line 110).

**Source:** Issue python/typeshed#9329, the redis-py 4.3.5...4.4.0 diff it links.

<!-- finding id=redis-cluster/retry-accessors head=55dfb451101480275ae05f2f08d1a899a691a77d priority=P2 action=must-fix blocking=true kind=requirement fix=stubs/redis/redis/cluster.pyi:59 -->

