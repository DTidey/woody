# Test Plan: candle-series-recent-window

Path: `docs/test-plans/18-candle-series-recent-window.md`
Spec: `docs/specs/18-candle-series-recent-window.md`

## What changed
- `backend/app/api/routes/candles.py`: `_load_candle_series` now aggregates `max(timestamp)` per series over the last 7 days (`SERIES_LOOKBACK_MS`), with the lower bound rendered as an inline bigint literal, and caches successful results for `SERIES_CACHE_TTL_SECONDS = 600` behind a lock. The recursive index-jump query is removed.
- `backend/tests/test_candles_route.py`: autouse fixture clears the series cache and dependency overrides; new tests for the SQL bound, cache hit, cache expiry, and error non-caching.

## Acceptance criteria coverage
- AC1: `test_list_candle_series_renders_lookback_bound_as_integer_literal` freezes `_now_ms`, compiles the executed statement with the psycopg dialect (`render_postcompile`), and asserts `c.timestamp >= <now_ms - 7 days>` as an integer literal, no `%(since_ms)s` placeholder, `max(c.timestamp)`, and no `RECURSIVE`. A manual check against a SQLite engine confirmed `literal_execute` renders the value inline at execution time too.
- AC2: `test_list_candle_series_returns_distinct_pairs` (existing, unchanged assertions) plus the `ORDER BY` assertion in the AC1 test.
- AC3: `test_list_candle_series_cache_hit_within_ttl` (TTL - 1 s: one query), `test_list_candle_series_cache_expires_after_ttl` (exactly TTL: second query), `test_list_candle_series_does_not_cache_errors` (two 500s both hit the DB; a later healthy session is queried and returns data).
- AC4: Review: no changes under `backend/alembic` or to models.
- AC5: All tests above use fake sessions; the autouse `_reset_series_cache` fixture makes test order irrelevant.
- AC6: Spec documents the trade-off and security disposition; `make lint`, `make test`, `make security` pass.

## Edge cases
- From spec:
  - Empty result is cached (valid answer; self-heals within 10 minutes).
  - Cache entry exactly at TTL is treated as expired.
  - DB errors propagate as HTTP 500 and are not cached.
- Additional adversarial cases:
  - A cached list is returned as a copy, so callers cannot mutate the cached list.
  - The monotonic clock is used, so wall-clock jumps do not extend or shorten the TTL.
  - Concurrent cold requests serialise on the lock and reuse one query result (not unit-tested; covered by design review).

## Notes
- Flaky risks: None; both clocks are monkeypatched.
- Determinism considerations: No network or real DB. Production timings are recorded in the spec's Measurements section and are not asserted in tests.
