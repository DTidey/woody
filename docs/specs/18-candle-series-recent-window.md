# Candle Series Recent Window

**Spec file:** `docs/specs/18-candle-series-recent-window.md`
**Spec slug:** candle-series-recent-window
**Status:** Done
**Owner:** Claude
**Date:** 2026-11-22

## Problem statement
- `GET /api/candles/series` times out in production, so the frontend (which calls it first) never loads.
- Production `public.candle` is a TimescaleDB 2.30 hypertable on PostgreSQL 17: 377 chunks (7-day chunk interval on the bigint epoch-ms `timestamp` column), 372 compressed (segmentby `exchange, symbol, timeframe`; orderby `timestamp DESC`), newest 5 uncompressed, ~373M rows. Indexes: unique btree `(exchange, symbol, timeframe, timestamp)` and btree `(timestamp DESC)`.
- The recursive "index-jump" query in `backend/app/api/routes/candles.py::_load_candle_series` merge-appends every chunk for each step. As the read-only role `woody_ro` it is cancelled by the role's 30 s `statement_timeout`; as superuser it ran for over 3 minutes without finishing.
- `GET /api/candles` (per-series fetch) is unaffected (16 ms).

## Scope
In scope:
- Replace the recursive query with an aggregate over a recent time window (7 days) that TimescaleDB can satisfy with plan-time chunk exclusion.
- Render the window lower bound as an inline integer literal.
- Add a short, thread-safe, in-process cache of successful results.
- Route tests in `backend/tests/test_candles_route.py`.
- `CHANGELOG.md` entry under `## Unreleased`.

Out of scope / non-goals:
- Any DB schema, index, compression policy, or Alembic migration change (the role is read-only with `SELECT` on `public.candle` only).
- Changing `GET /api/candles` or the `CandleSeriesResponse` model.
- Frontend changes.
- Cross-process/shared caching (e.g. Redis), cache invalidation on import.
- Creating a release.

## Assumptions
- Every actively imported series has at least one candle in the last 7 days. 7 days (rather than 3) lets stock series survive weekends/holidays and a missed nightly import.
- Server clock is roughly correct (UTC epoch ms); small skew only shifts the window edge.
- Each API worker process holding its own cache is acceptable.

## Ambiguities surfaced
- Empty result caching: an empty list from a successful query is cached for the TTL like any other success. Decision: cache it, because it is still a valid answer and avoids hammering the DB on every page load when there is no recent data; it self-heals after at most 10 minutes.
- Concurrent cold loads: the cache lock is held while the query runs (single-flight), so concurrent requests during a cold load wait for one query instead of all issuing it. Waiters are bounded by the query time (and the role's 30 s `statement_timeout`).

## Proposed behavior / API
### Public interface
- Functions/classes/modules affected:
  - `backend/app/api/routes/candles.py`: `_load_candle_series`, new `SERIES_LOOKBACK_MS`, `SERIES_CACHE_TTL_SECONDS`, `_clear_series_cache()`, `_now_ms()`, `_monotonic()`.
  - `backend/tests/test_candles_route.py`
- CLI entry points: none.

### Inputs / outputs
- Inputs: `GET /api/candles/series` (no parameters).
- Outputs: unchanged JSON list of `{exchange, symbol, timeframe, latest_timestamp}` ordered by `latest_timestamp DESC, exchange, symbol, timeframe`.
- Error handling: DB exceptions propagate as before (HTTP 500); they are not cached, so the next request retries.

### Examples
```sql
SELECT c.exchange, c.symbol, c.timeframe, max(c.timestamp) AS latest_timestamp
FROM public.candle c
WHERE c.timestamp >= 1763164800000   -- now_ms - 7 days, inline bigint literal
GROUP BY c.exchange, c.symbol, c.timeframe
ORDER BY latest_timestamp DESC, c.exchange, c.symbol, c.timeframe;
```

## Acceptance criteria
- AC1: `/api/candles/series` lists only series with at least one candle whose `timestamp >= now_ms - SERIES_LOOKBACK_MS` (`SERIES_LOOKBACK_MS = 7 * 24 * 60 * 60 * 1000`, module constant), with `latest_timestamp = max(timestamp)` for that series; the bound is computed in Python from the current time in epoch ms and rendered into the SQL as an inline integer literal (SQLAlchemy `bindparam(..., type_=BigInteger, literal_execute=True)`), not a server-side bind parameter.
- AC2: Response shape and ordering are unchanged: a list of `{exchange, symbol, timeframe, latest_timestamp}` ordered by `latest_timestamp DESC, exchange, symbol, timeframe`; `CandleSeriesResponse` is unchanged.
- AC3: Successful results (including an empty list) are cached in-process for `SERIES_CACHE_TTL_SECONDS = 600` measured with a monotonic clock; access is guarded by a lock; exceptions are not cached; `_clear_series_cache()` resets the cache for tests.
- AC4: No DB schema, index, or Alembic migration changes; the query only needs `SELECT` on `public.candle`.
- AC5: Tests in `backend/tests/test_candles_route.py` (fake session, no real DB) cover: unchanged shape/order; executed SQL contains the lower bound as an integer literal equal to frozen `now_ms - 7 days` when compiled with the psycopg dialect; a second call within the TTL does not query; a call after TTL expiry queries again; a DB exception is not cached. The cache is cleared between tests.
- AC6: The trade-off (series with no candles in the last 7 days are no longer listed, while `/api/candles` still serves them directly) and the security disposition are documented in this spec, and `make lint`, `make test`, and `make security` pass.

## Trade-offs
- Series with no candles in the last 7 days (delisted symbols, stopped imports) no longer appear in `/api/candles/series`. `GET /api/candles?exchange=..&symbol=..&timeframe=..` still returns their data if called directly.
- The list can be up to 10 minutes stale (new series appear, `latest_timestamp` advances) because of the cache. The frontend loads candles per series via `/api/candles`, so the chart data itself is not stale.
- `latest_timestamp` is still the true latest per listed series, because all newer data lies inside the window.

## Measurements
Measured on the live DB as `woody_ro`, 316 series returned (Binance Perpetual Futures 1m x308, 4h x3, Massive Stocks 1m x5):
- Before (recursive index-jump query): cancelled by the 30 s `statement_timeout` as `woody_ro` (30016 ms); over 3 minutes without finishing as superuser.
- After, 7-day window with inline literal: ~549 ms warm, ~848 ms cold; 2 uncompressed chunks scanned, 375 of 377 excluded at plan time.
- For reference, 3-day window: 514 ms warm, 3380 ms cold, 1 chunk scanned.
- Pitfall: with a server-side bind parameter and a generic plan (psycopg 3 auto-prepares after 5 executions on a connection) planning takes ~1 s and execution ~3.4 s (runtime chunk exclusion + parallel index scan). Hence the inline literal, which forces plan-time chunk exclusion and gives every execution distinct SQL text, so no generic plan is reused.

## Security considerations
- Auth/authz impact: None; endpoint access is unchanged.
- Input handling or injection risk: None. The only value inlined into SQL is an `int` computed server-side from the clock, rendered by SQLAlchemy's `BigInteger` literal processor; no request input reaches the SQL.
- Secrets or credential handling: None.
- Data exposure or privacy impact: None new; the cache holds only the public series list already returned by the endpoint.
- File system access impact: None.
- Network or external service impact: Reduces DB load (fewer, cheaper queries).
- Dependency or supply-chain impact: None; no dependency changes.
- Security notes for reviewers/testers: Confirm the literal comes only from `_now_ms()` and that exceptions are never cached. No meaningful new exposure.

## Edge cases
- No candles in the window -> empty list, cached for the TTL.
- DB error / statement timeout -> HTTP 500, not cached; next request retries.
- Cache entry exactly at TTL -> treated as expired (refetch).
- Concurrent requests on a cold cache -> one query; others wait on the lock and reuse the result.

## Test guidance
- AC1 -> `test_list_candle_series_renders_lookback_bound_as_integer_literal`
- AC2 -> `test_list_candle_series_returns_distinct_pairs`
- AC3 -> `test_list_candle_series_cache_hit_within_ttl`, `test_list_candle_series_cache_expires_after_ttl`, `test_list_candle_series_does_not_cache_errors`
- AC4 -> review: no files under `backend/alembic` changed
- AC5 -> all of the above plus the autouse cache-clearing fixture
- AC6 -> this spec; `make lint`, `make test`, `make security`

## Decision log
- 2026-11-22: Chose a 7-day window over 3 days so stock series survive weekends/holidays and one missed import; cost difference is negligible (~0.55 s vs ~0.51 s warm).
- 2026-11-22: Chose `literal_execute=True` over string formatting so SQLAlchemy renders the bigint literal and bandit needs no `# nosec`.
- 2026-11-22: Hold the cache lock during the query (single-flight) to avoid a thundering herd on cold loads.
