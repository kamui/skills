# Review payload — `python/typeshed#9458` (rendered only; publication disabled)

This file is the review exactly as it would have been submitted with `gh api --method POST repos/python/typeshed/pulls/9458/reviews`, `event: COMMENT`, `commit_id: 55dfb451101480275ae05f2f08d1a899a691a77d`, posting identity `kamui` — had this cell's run conditions permitted publication. They do not (target is merged; this is a retrospective run with publication disabled), so nothing below was ever sent anywhere.

## Review body (the summary)

**Mode: retrospective review of a merged pull request.** `python/typeshed#9458` merged on 2023-01-05T15:25:11Z; this review was produced after the fact and evaluates the code as merged. Publication is disabled for this run; what follows is rendered, not posted.

**Changes Requested (advisory)** — 4 blocking findings, 0 open questions.

Code: Passed (the Code finder confirmed 2 candidates, but both describe the same defects as Requirements candidates and were merged into the Requirements-axis findings below per `verify.md` § Deduplicate — no Code-axis finding stands on its own). Requirements: Findings — 4 blocking, 4 optional; issue alignment: available (originating reference [`python/typeshed#9329`](https://github.com/python/typeshed/pull/9329), itself a closed, unmerged pull request whose body and comments are the spec source, per `Closes #9329` in this pull request's body).

Reviewed `55dfb4511` against `main` (merge-base `8365b1aa`; the recorded base SHA `70025c37` differs because `main` moved before merge — reviewed against the merge-base, which is what this pull request means). Coverage: **incomplete**. Both finders reviewed and gave a reason for all 10 manifest entries, but: (a) the Requirements finder explicitly named five upstream command submodules (`redis/commands/{bf,graph,json,search,timeseries}`) and `redis/ocsp.py` as not symbol-by-symbol audited against their 4.3.5→4.4.0 upstream diffs, since none of their `.pyi` peers are in this pull request's changed-file manifest; (b) the Code finder's report failed the mechanical shape validator (`validate_finder_report.py`) twice — see the run report's Notes for the disclosed judgment call made to unblock the run rather than issue a third dispatch. Neither gap changes the status below the `Changes Requested` already forced by unsettled `must-fix` findings.

This is a stub-completeness bump (redis-py 4.3.5→4.4.0) that gets most of the surface right — every constructor and signature change in the diff was checked line-for-line against the real library at both tags and matches. What drives the status is one consistent failure mode repeated four times: a public runtime member that changed shape in 4.4.0 — a renamed method, a new module function, two new accessor methods, a new command — was left out of the stub entirely. Fix the `can_read`→`can_read_destructive` rename and the missing `bitfield_ro`/`get_retry`/`set_retry`/`default_backoff` additions first; the other four findings are lower-priority instances of the same shape, two of them (`MaxConnectionsError`, the top-level `CredentialProvider` re-export) on files this pull request never touched at all.

- [Requirements] [must-fix] [P1] — New `default_backoff()` and its top-level re-export are entirely missing — anchor [`stubs/redis/redis/backoff.pyi:28`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L28); fix [`stubs/redis/redis/backoff.pyi:29`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L29)
- [Requirements] [must-fix] [P1] — `can_read` renamed to `can_read_destructive` upstream, only removed in stub — anchor `stubs/redis/redis/asyncio/connection.pyi:49` (merge-base); fix [`stubs/redis/redis/asyncio/connection.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/asyncio/connection.pyi)
- [Requirements] [must-fix] [P1] — New `BITFIELD_RO` command (`bitfield_ro`) is entirely unstubbed — anchor [`stubs/redis/METADATA.toml:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/METADATA.toml?plain=1#L1); fix [`stubs/redis/redis/commands/core.pyi:290`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/commands/core.pyi?plain=1#L290)
- [Requirements] [must-fix] [P1] — `get_retry`/`set_retry` accessors missing on `RedisCluster` and both `Redis` classes — anchor [`stubs/redis/redis/cluster.pyi:66`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L66); fix [`stubs/redis/redis/cluster.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi)
- [Requirements] [consider] [P2] — `CredentialProvider`/`UsernamePasswordCredentialProvider` missing from `redis.__init__` — anchor [`stubs/redis/redis/credentials.pyi:3`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/credentials.pyi?plain=1#L3); fix [`stubs/redis/redis/__init__.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi)
- [Requirements] [consider] [P2] — New `MaxConnectionsError` exception class is not stubbed — anchor [`stubs/redis/METADATA.toml:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/METADATA.toml?plain=1#L1); fix [`stubs/redis/redis/exceptions.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/exceptions.pyi)
- [Requirements] [consider] [P2] — New `RedisCluster.replace_default_node` method is unstubbed — anchor [`stubs/redis/METADATA.toml:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/METADATA.toml?plain=1#L1); fix [`stubs/redis/redis/cluster.pyi:93`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/cluster.pyi?plain=1#L93)
- [Requirements] [consider] [P3] — New `deprecated_function`/`warn_deprecated` helpers are unstubbed — anchor [`stubs/redis/METADATA.toml:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/METADATA.toml?plain=1#L1); fix [`stubs/redis/redis/utils.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/utils.pyi)

Counts: Requirements 4 must-fix, 4 consider (0 questions, 0 disputed). Code 0 (both its candidates carried forward under the Requirements ids above). 2 candidates refuted (0 — none were refuted this round; all 10 raised candidates were confirmed, and 2 pairs collapsed into 2 of the 8 findings above via dedup).

## Observations

These are accurate observations, not findings — no action is requested.

- The whole `redis.asyncio.cluster` module (upstream `redis/asyncio/cluster.py`) has no corresponding `.pyi` stub in this package; this predates the reviewed release bump (the module is unchanged between the 4.3.5 and 4.4.0 upstream tags) and is not something this pull request introduced (`redis-py-4.3.5/redis/asyncio/cluster.py:1`).
- `stubs/redis/redis/asyncio/sentinel.pyi:18` correctly adds `# type: ignore[override]` to `SentinelManagedConnection.read_response`, because upstream's base `Connection.read_response` gained a `timeout` parameter in 4.4.0 that the sentinel override still lacks — a real signature divergence the pull request documents rather than a defect.

<!-- review-run workflow=v2a-1 head=55dfb451101480275ae05f2f08d1a899a691a77d base-ref=main base-sha=8365b1aaefd46d506ca0dfe73e9721da2d03c566 merge-base=8365b1aaefd46d506ca0dfe73e9721da2d03c566 issues=python/typeshed#9329 coverage=incomplete -->

---

## Line comments (per-finding, in index order)

Each of the following would be submitted as one entry in the batched review call's `comments[]`, `side: RIGHT` unless noted, attached at its rendered anchor line.

### 1 — `stubs/redis/redis/backoff.pyi:28` (RIGHT)

**[Requirements] [must-fix] [P1] `default_backoff()` and its top-level re-export are entirely missing**

Upstream `redis/backoff.py` 4.4.0 adds `def default_backoff(): return EqualJitterBackoff()` (absent at 4.3.5), and both `redis/__init__.py` and `redis/asyncio/__init__.py` add it to their imports and `__all__`. This pull request updates the four backoff classes' `__init__` defaults (`stubs/redis/redis/backoff.pyi:16-28`, correctly matching upstream's new `DEFAULT_CAP`/`DEFAULT_BASE`) but never adds `default_backoff` anywhere in the stub tree.

**Triggers when**: code written against redis-py 4.4.0 calls `redis.default_backoff()` or `redis.asyncio.default_backoff()` — the documented way to get the library's own default retry backoff — and a type checker using this stub rejects it as an unknown attribute, even though it is valid runtime code.

**Change**: add `def default_backoff() -> EqualJitterBackoff: ...` to `stubs/redis/redis/backoff.pyi` (after line 28), and re-export it (`default_backoff` in `__all__` and import) from `stubs/redis/redis/__init__.pyi` and `stubs/redis/redis/asyncio/__init__.pyi`, matching upstream.

<!-- finding id=requirements/redis-backoff/default-backoff-missing axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/backoff.pyi:29 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 2 — `stubs/redis/redis/asyncio/connection.pyi:49` (LEFT, merge-base)

**[Requirements] [must-fix] [P1] `can_read` renamed to `can_read_destructive` upstream, only removed in stub**

Upstream `redis/asyncio/connection.py` renames `async def can_read(self, timeout: float) -> bool` to `async def can_read_destructive(self) -> bool` (no `timeout` param) on `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` between 4.3.5 and 4.4.0 — it is not removed, and remains a public, non-underscore, actively-used member (`redis/asyncio/connection.py:1369,1374,1576,1581` in the 4.4.0 tree). This pull request's diff to `stubs/redis/redis/asyncio/connection.pyi` deletes `can_read` from all four classes (the line this comment anchors, at the merge-base) but adds no `can_read_destructive` anywhere; a full-tree grep confirms it.

**Triggers when**: code holding an async `Connection`/parser instance calls `.can_read_destructive()` — the only name the real 4.4.0 library exposes for this capability — and a type checker using this stub rejects it as an unknown attribute.

**Change**: add `async def can_read_destructive(self) -> bool: ...` to `BaseParser`, `PythonParser`, `HiredisParser`, and `Connection` in `stubs/redis/redis/asyncio/connection.pyi`.

<!-- finding id=requirements/redis-asyncio-connection/can-read-destructive-dropped axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/asyncio/connection.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 3 — `stubs/redis/METADATA.toml:1` (RIGHT)

**[Requirements] [must-fix] [P1] New `BITFIELD_RO` command (`bitfield_ro`) is entirely unstubbed**

Upstream `redis/commands/core.py` 4.4.0 adds `def bitfield_ro(self, key, encoding, offset, items=None) -> ResponseT` to `BasicKeyCommands` (shared by both `Redis` and `AsyncRedis`), absent at 4.3.5. `stubs/redis/redis/commands/core.pyi` was touched by this pull request (the unrelated `xautoclaim`/`StreamIdT` fix at lines 821 and 864) but neither `BasicKeyCommands` (line 290) nor `AsyncBasicKeyCommands` (line 397) gained a `bitfield_ro` method. This comment anchors to the version-bump line because the omission touches no line this diff actually changed.

**Triggers when**: code calls `redis_client.bitfield_ro(...)` — the documented read-only variant of `BITFIELD`, real and callable on both the sync and async client in 4.4.0 — and a type checker using this stub rejects it as an unknown attribute, on either client.

**Change**: add a `bitfield_ro` method to `BasicKeyCommands` (`stubs/redis/redis/commands/core.pyi:290`, beside the existing `bitfield`) and to `AsyncBasicKeyCommands` (line 397).

<!-- finding id=requirements/redis-commands-core/bitfield-ro-missing axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/commands/core.pyi:290 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 4 — `stubs/redis/redis/cluster.pyi:66` (RIGHT)

**[Requirements] [must-fix] [P1] `get_retry`/`set_retry` accessors missing on `RedisCluster` and both `Redis` classes**

Upstream 4.4.0 adds `def get_retry(self) -> Optional["Retry"]` and `def set_retry(self, retry: "Retry") -> None` to `RedisCluster` (`redis/cluster.py:701,704`), to sync `Redis` (`redis/client.py:1051,1054`), and to async `Redis` (`redis/asyncio/client.py:279,282`) — none present at 4.3.5. This pull request added the companion `retry: Retry | None = ...` constructor parameter to `RedisCluster.__init__` at the anchored line, but the accessor pair was added to none of the three classes; a repo-wide grep for `get_retry`/`set_retry` returns nothing.

**Triggers when**: code calls `.get_retry()`/`.set_retry(r)` on a `Redis` or `RedisCluster` instance — the documented way to read or replace a client's retry policy after construction, added in 4.4.0 — and a type checker using this stub rejects it as an unknown attribute.

**Change**: add `get_retry`/`set_retry` to `RedisCluster` in `stubs/redis/redis/cluster.pyi`, to `Redis` in `stubs/redis/redis/client.pyi`, and to `Redis` in `stubs/redis/redis/asyncio/client.pyi`.

<!-- finding id=requirements/redis-retry-accessors/get-set-retry-missing axis=requirements action=must-fix priority=P1 fix=stubs/redis/redis/cluster.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 5 — `stubs/redis/redis/credentials.pyi:3` (RIGHT)

**[Requirements] [consider] [P2] `CredentialProvider`/`UsernamePasswordCredentialProvider` missing from `redis.__init__`**

Upstream `redis/__init__.py` 4.4.0 adds `from redis.credentials import CredentialProvider, UsernamePasswordCredentialProvider` and both names to `__all__` (absent at 4.3.5). This pull request adds `stubs/redis/redis/credentials.pyi` (the anchored new file) but never touches `stubs/redis/redis/__init__.pyi`, whose `__all__` and re-export block still lack both names.

**Triggers when**: code does `redis.CredentialProvider` or `redis.UsernamePasswordCredentialProvider` (the top-level spelling upstream now supports) and a type checker rejects it as an unknown attribute — though `from redis.credentials import CredentialProvider` (the only path this stub supports) works.

**Change**: add `from .credentials import CredentialProvider as CredentialProvider, UsernamePasswordCredentialProvider as UsernamePasswordCredentialProvider` (or equivalent) and both names to `__all__` in `stubs/redis/redis/__init__.pyi`.

Closing this without action is a correct response.

<!-- finding id=requirements/redis-init/credential-provider-not-reexported axis=requirements action=consider priority=P2 fix=stubs/redis/redis/__init__.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 6 — `stubs/redis/METADATA.toml:1` (RIGHT)

**[Requirements] [consider] [P2] New `MaxConnectionsError` exception class is not stubbed**

Upstream `redis/exceptions.py` 4.4.0 adds `class MaxConnectionsError(ConnectionError): ...` (absent at 4.3.5). `stubs/redis/redis/exceptions.pyi` was not touched by this pull request at all and has no `MaxConnectionsError` class. This comment anchors to the version-bump line because the omission touches no line this diff actually changed.

**Triggers when**: code does `except redis.exceptions.MaxConnectionsError:` — the documented way to catch a connection-pool-exhaustion error introduced in 4.4.0 — and a type checker rejects the reference as an unknown attribute.

**Change**: add `class MaxConnectionsError(ConnectionError): ...` to `stubs/redis/redis/exceptions.pyi`.

Closing this without action is a correct response.

<!-- finding id=requirements/redis-exceptions/max-connections-error-missing axis=requirements action=consider priority=P2 fix=stubs/redis/redis/exceptions.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 7 — `stubs/redis/METADATA.toml:1` (RIGHT)

**[Requirements] [consider] [P2] New `RedisCluster.replace_default_node` method is unstubbed**

Upstream `redis/cluster.py` 4.4.0 adds `def replace_default_node(self, target_node: "ClusterNode" = None) -> None` to `RedisCluster` (absent at 4.3.5), a companion to the existing `get_default_node`/`set_default_node` pair already present in the stub at `stubs/redis/redis/cluster.pyi:92-93`. It is not stubbed. This comment anchors to the version-bump line because the omission touches no line this diff actually changed.

**Triggers when**: code calls `cluster.replace_default_node()` — the documented way to force a new default node without naming one — and a type checker rejects it as an unknown attribute.

**Change**: add `def replace_default_node(self, target_node: ClusterNode | None = ...) -> None: ...` to `RedisCluster` in `stubs/redis/redis/cluster.pyi`, beside `get_default_node`/`set_default_node` at line 93.

Closing this without action is a correct response.

<!-- finding id=requirements/redis-cluster/replace-default-node-missing axis=requirements action=consider priority=P2 fix=stubs/redis/redis/cluster.pyi:93 head=55dfb451101480275ae05f2f08d1a899a691a77d -->

### 8 — `stubs/redis/METADATA.toml:1` (RIGHT)

**[Requirements] [consider] [P3] New `deprecated_function`/`warn_deprecated` helpers are unstubbed**

Upstream `redis/utils.py` adds `def warn_deprecated(name, reason="", version="", stacklevel=2)` and `def deprecated_function(reason="", version="", name=None)`; `deprecated_function` is used in practice as a decorator on several public methods in `redis/commands/{search,json,bf}/commands.py`. `stubs/redis/redis/utils.pyi` (untouched by this pull request) has neither. The verifier corrected the finder's premise: these helpers are byte-identical between the 4.3.5 and 4.4.0 upstream tags, so this is a pre-existing gap this bump did not introduce, not a regression — kept as `consider`/`P3`, the most conservative rating available, rather than raised.

**Triggers when**: code does `from redis.utils import deprecated_function` or `warn_deprecated` directly (uncommon — these are internal library helpers) and a type checker rejects the import as an unknown attribute.

**Change**: add `def warn_deprecated(name, reason: str = ..., version: str = ..., stacklevel: int = ...) -> None: ...` and `def deprecated_function(reason: str = ..., version: str = ..., name: str | None = ...) -> Callable[..., Incomplete]: ...` (or equivalent) to `stubs/redis/redis/utils.pyi`.

Closing this without action is a correct response.

<!-- finding id=requirements/redis-utils/deprecated-function-missing axis=requirements action=consider priority=P3 fix=stubs/redis/redis/utils.pyi head=55dfb451101480275ae05f2f08d1a899a691a77d -->
