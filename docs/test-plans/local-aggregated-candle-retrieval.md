# Local Aggregated Candle Retrieval

## Summary
- Replaced the backend `/api/candles` Jesse runtime path with a local candle aggregation service built from stored 1m rows.
- Preserved the public query shape of `exchange`, `symbol`, `timeframe`, and `limit`.
- Made candle `id` optional and preserved millisecond timestamps for synthesized candles.

## Acceptance criteria coverage
- AC1: Inspect `backend/app/api/routes/candles.py` and `backend/app/services/candles.py` to confirm `/api/candles` reads from stored 1m candles and does not call Jesse at runtime.
- AC2: Inspect `backend/app/services/candles.py` and `backend/tests/test_candle_service.py` to confirm higher timeframes are aggregated with UTC epoch-aligned buckets, incomplete buckets are dropped, and the final payload is trimmed newest-first.
- AC3: Inspect `backend/app/api/routes/candles.py`, `backend/app/services/candles.py`, and `backend/tests/test_candles_route.py` to confirm the response preserves the existing candle fields, keeps millisecond timestamps, and allows `id: null` for synthesized candles.

## Validation run
- `make lint`
- `make test`

## Risks
- Large `limit` values on very large timeframes may require loading many 1m rows, so extremely large aggregation windows may still need follow-up optimization.
