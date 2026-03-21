# Local Aggregated Candle Retrieval

**Spec slug:** local-aggregated-candle-retrieval
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-19

## Problem statement
- The backend currently needs higher-timeframe candles, but the database only stores 1 minute rows.
- A direct runtime dependency on Jesse adds project-layout, `.env`, Redis, and bootstrap assumptions that are much broader than the candle aggregation behavior we actually need.
- This matters because the API should stay simple and reliable while still synthesizing higher timeframes from 1m source candles.

## Scope
In scope:
- Replace the backend's direct `GET /api/candles` data retrieval path with a local aggregation service built on stored 1m candles.
- Preserve the existing public route shape of `GET /api/candles?exchange=...&symbol=...&timeframe=...&limit=...`.
- Aggregate supported higher timeframes from 1m candles inside this codebase.
- Normalize aggregated candle output into the API response model used by the frontend.
- Document and test timestamp unit, ordering, and partial-bucket behavior.

Out of scope / non-goals:
- Changing `/api/candles/series` to use a different source.
- Adding new query parameters such as `start`, `end`, or pagination.
- Reworking frontend candle selection behavior.
- Preserving a runtime dependency on Jesse.

## Assumptions
- The database stores reliable 1m candles for each exchange and symbol pair.
- The frontend should continue calling the same `/api/candles` endpoint shape after this change.
- A request for `timeframe=1m` should return rows compatible with the current frontend payload.
- Higher-timeframe buckets should be built using UTC epoch-aligned bucket boundaries.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `backend/app/api/routes/candles.py`
  - `backend/app/services/candles.py`
  - `backend/tests/test_candle_service.py`
  - `backend/tests/test_candles_route.py`
  - `docs/test-plans/06-local-aggregated-candle-retrieval.md`
  - `.ai/pr-description/06-local-aggregated-candle-retrieval.md`

### Inputs / outputs
- Inputs:
  - Request query parameters `exchange`, `symbol`, `timeframe`, and `limit`
  - Available 1m candle rows in the application database
- Outputs:
  - A list of candle objects for the requested exchange, symbol, and timeframe
  - Candles ordered newest-first to preserve current frontend expectations
- Error handling:
  - If required filters are missing, the route should continue to reject the request through validation.
  - If the requested timeframe is unsupported, the backend should return a clear client-facing error instead of silently falling back to raw 1m data.
  - If the source 1m history is incomplete, the backend may return fewer candles than requested rather than returning partial higher-timeframe buckets.

### Examples
```text
GET /api/candles?exchange=binance&symbol=BTC-USDT&timeframe=1h&limit=200
-> backend loads recent 1m BTC-USDT candles
-> backend groups them into 1h buckets using UTC epoch-aligned boundaries
-> backend drops incomplete 1h buckets
-> backend returns up to 200 normalized BTC-USDT 1h candles ordered newest-first

GET /api/candles?exchange=binance&symbol=BTC-USDT&timeframe=1m&limit=200
-> backend loads recent 1m BTC-USDT candles directly
-> backend returns 200 normalized BTC-USDT 1m candles ordered newest-first
```

## Acceptance criteria
- AC1: `GET /api/candles` retrieves source rows from stored 1m candles and synthesizes supported higher timeframes locally instead of calling Jesse at runtime.
- AC2: The backend uses UTC epoch-aligned bucket aggregation for supported timeframes, trims the normalized response to the requested `limit`, preserves newest-first ordering, and drops incomplete higher-timeframe buckets.
- AC3: The API response remains compatible with the existing frontend contract for `exchange`, `symbol`, `timeframe`, OHLCV fields, and millisecond timestamps, and the implementation keeps `id` optional for synthesized candles.

## Edge cases
- Requested higher timeframes such as `1h` or `4h` must be synthesized from 1m source candles rather than relying on pre-aggregated DB rows.
- Requests near the live edge may return fewer candles than requested if the latest bucket is incomplete.
- The same source series may include gaps in 1m history; incomplete higher-timeframe buckets should be dropped rather than emitted with partial data.
- Aggregated candles do not have a stable database primary key and should use `id: null`.
- Timestamp units should remain in milliseconds so the frontend can continue normalizing them safely.

## Test guidance
- AC1 -> route/service test that verifies `/api/candles` reads from 1m source rows and no longer depends on Jesse runtime imports
- AC2 -> service test covering bucket aggregation, newest-first ordering, limit trimming, and incomplete-bucket dropping
- AC3 -> API response test covering normalized candle fields, millisecond timestamps, and `id: null` behavior for aggregated rows

## Decision log
- 2026-03-19: Chose a new backend-focused spec because the primary behavior change is the candle retrieval source and normalization contract.
- 2026-03-19: Preserved the public `/api/candles` query shape so the frontend does not need to change.
- 2026-03-19: Made candle `id` optional because synthesized higher-timeframe candles do not map one-to-one to persisted DB rows.
- 2026-03-19: Preserved millisecond timestamps in the backend response because the frontend already normalizes that unit safely.
- 2026-03-19: Replaced the Jesse runtime dependency with a local aggregation service because the app only needs a small slice of candle aggregation behavior and Jesse's broader bootstrap assumptions made the integration fragile.
