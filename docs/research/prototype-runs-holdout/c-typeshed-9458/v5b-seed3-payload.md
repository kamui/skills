**Changes Requested (advisory)** — 2 must-fix findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Bump the `redis` typeshed stub from redis-py 4.3.5 to 4.4.0, tracking the closed stubsabot PR #9329 and its linked upstream compare.

**Issue fit:** Partial — every changed-file hunk in this PR accurately reflects the corresponding redis-py 4.4.0 signature (verified against the pinned 4.3.5/4.4.0 source trees), but the bump omits two of the release's new top-level exports.

**Coverage:** Complete merge-base diff reviewed (10 files); every hunk cross-checked against the pinned redis-py 4.3.5 and 4.4.0 source; all five `__init__.py`-shaped files in the upstream compare checked for `__all__` completeness.

**Reviewed:** `55dfb451` against merge-base `8365b1aa`.

## Unanchored findings

**[P2] [must-fix] Re-export `CredentialProvider` and `UsernamePasswordCredentialProvider` from `redis/__init__.pyi`**

**Triggers when:** Code imports `CredentialProvider` or `UsernamePasswordCredentialProvider` from the top-level `redis` package, or writes `redis.CredentialProvider`/`redis.UsernamePasswordCredentialProvider` — both valid at runtime, since redis-py 4.4.0's `redis/__init__.py` imports both from `redis.credentials` and lists both in `__all__`.

**Impact:** A type checker reports both names as missing from the `redis` module, a false positive against code that runs correctly on the bumped version.

**Change:** In `stubs/redis/redis/__init__.pyi`, import `CredentialProvider` and `UsernamePasswordCredentialProvider` from `.credentials` and add both names to `__all__`, matching `redis/__init__.py`'s 4.4.0 export list.

**Source:** `CONTRIBUTING.md`, "What to include": "All objects included in `__all__` (if present)" must always be stubbed.

anchor [`stubs/redis/redis/credentials.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/credentials.pyi) (file); fix [`stubs/redis/redis/__init__.pyi:1`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/__init__.pyi?plain=1#L1)

<!-- finding id=typeshed-redis/init-credential-provider-reexport head=55dfb451101480275ae05f2f08d1a899a691a77d priority=P2 action=must-fix blocking=true kind=requirement fix=stubs/redis/redis/__init__.pyi:1 -->

**[P2] [must-fix] Stub the new `default_backoff()` function and its re-exports**

**Triggers when:** Code imports `default_backoff` from `redis.backoff`, from the top-level `redis` package, or from `redis.asyncio` — all valid at runtime, since redis-py 4.4.0 adds `default_backoff()` to `redis/backoff.py` and lists it in `__all__` in both `redis/__init__.py` and `redis/asyncio/__init__.py`.

**Impact:** A type checker reports `default_backoff` as undefined at all three import sites, a false positive against code that runs correctly on the bumped version.

**Change:** In `stubs/redis/redis/backoff.pyi`, add `default_backoff`'s signature (it returns an `AbstractBackoff` instance, specifically `EqualJitterBackoff()`); then import and list it in `__all__` in both `stubs/redis/redis/__init__.pyi` and `stubs/redis/redis/asyncio/__init__.pyi`.

**Source:** `CONTRIBUTING.md`, "What to include": "All objects included in `__all__` (if present)" must always be stubbed.

anchor [`stubs/redis/redis/backoff.pyi`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi) (file); fix [`stubs/redis/redis/backoff.pyi:29`](https://github.com/python/typeshed/blob/55dfb451101480275ae05f2f08d1a899a691a77d/stubs/redis/redis/backoff.pyi?plain=1#L29)

<!-- finding id=typeshed-redis/backoff-default-backoff-missing head=55dfb451101480275ae05f2f08d1a899a691a77d priority=P2 action=must-fix blocking=true kind=requirement fix=stubs/redis/redis/backoff.pyi:29 -->

<!-- review-run head=55dfb451101480275ae05f2f08d1a899a691a77d base-ref=main base-sha=70025c372346288675437fc0bd273db84cc0b3d5 merge-base=8365b1aaefd46d506ca0dfe73e9721da2d03c566 workflow=v5b-1 context=62453b2c82386967adabff8652687099ad7a12ff8d74073279ef6818867eca33 issues=python/typeshed#9329 coverage=complete -->
