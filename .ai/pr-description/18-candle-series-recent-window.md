## Summary
- Fix `GET /api/candles/series` timing out in production (TimescaleDB hypertable, 377 mostly compressed chunks): list series from candles in the last 7 days with a plain `GROUP BY ... max(timestamp)` instead of the recursive index-jump query that touched every chunk.
- The window lower bound is rendered as an inline bigint literal (`literal_execute=True`) so TimescaleDB excludes chunks at plan time and psycopg never reuses a slow generic plan.
- Successful results are cached in-process for 10 minutes (lock-guarded, monotonic clock, errors not cached).
- Response shape and ordering are unchanged. Trade-off: series with no candles in the last 7 days are no longer listed (`/api/candles` still serves them directly).

## Spec
- Spec: `docs/specs/18-candle-series-recent-window.md`
- Test plan: `docs/test-plans/18-candle-series-recent-window.md`
- PR draft path: `.ai/pr-description/18-candle-series-recent-window.md`

## Acceptance criteria
- [x] AC1: `/api/candles/series` lists only series with at least one candle whose `timestamp >= now_ms - SERIES_LOOKBACK_MS` (`SERIES_LOOKBACK_MS = 7 * 24 * 60 * 60 * 1000`, module constant), with `latest_timestamp = max(timestamp)` for that series; the bound is computed in Python from the current time in epoch ms and rendered into the SQL as an inline integer literal (SQLAlchemy `bindparam(..., type_=BigInteger, literal_execute=True)`), not a server-side bind parameter.
- [x] AC2: Response shape and ordering are unchanged: a list of `{exchange, symbol, timeframe, latest_timestamp}` ordered by `latest_timestamp DESC, exchange, symbol, timeframe`; `CandleSeriesResponse` is unchanged.
- [x] AC3: Successful results (including an empty list) are cached in-process for `SERIES_CACHE_TTL_SECONDS = 600` measured with a monotonic clock; access is guarded by a lock; exceptions are not cached; `_clear_series_cache()` resets the cache for tests.
- [x] AC4: No DB schema, index, or Alembic migration changes; the query only needs `SELECT` on `public.candle`.
- [x] AC5: Tests in `backend/tests/test_candles_route.py` (fake session, no real DB) cover: unchanged shape/order; executed SQL contains the lower bound as an integer literal equal to frozen `now_ms - 7 days` when compiled with the psycopg dialect; a second call within the TTL does not query; a call after TTL expiry queries again; a DB exception is not cached. The cache is cleared between tests.
- [x] AC6: The trade-off (series with no candles in the last 7 days are no longer listed, while `/api/candles` still serves them directly) and the security disposition are documented in this spec, and `make lint`, `make test`, and `make security` pass.

## Security review
- [x] Security considerations were reviewed and updated in the linked spec
- [x] No meaningful security impact
- [ ] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [ ] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - The only inlined SQL value is an `int` from the server clock, rendered by SQLAlchemy's `BigInteger` literal processor; no request input reaches the SQL (bandit clean, no `# nosec`).
  - The cache holds only the public series list; exceptions are never cached.

## Measurements
Live DB, as read-only role `woody_ro`, 316 series returned (Binance Perpetual Futures 1m x308, 4h x3, Massive Stocks 1m x5):
- Before: recursive query cancelled by the 30 s `statement_timeout` (30016 ms) as `woody_ro`; over 3 minutes without finishing as superuser.
- After (7-day window, inline literal): ~0.55 s warm (549 ms), ~0.85 s cold (848 ms); 2 of 377 chunks scanned, 375 excluded at plan time.
- 3-day window for comparison: 514 ms warm, 3380 ms cold, 1 chunk.
- Generic-plan pitfall: with a server-side bind parameter after psycopg auto-prepares (5 executions), ~1 s planning + ~3.4 s execution (runtime chunk exclusion). Hence the inline literal.

## Validation
- [x] `make lint`
- [x] `make test` (40 passed)
- [x] `make security` (bandit clean, pip-audit no known vulnerabilities)

## GitHub checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`

## Changelog
- [x] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- Series without candles in the last 7 days disappear from the series list (by design); a longer import outage would hide series until data resumes.
- The series list can be up to 10 minutes stale, per API worker process.
- Timings were measured against production by hand; they are not asserted in CI.
