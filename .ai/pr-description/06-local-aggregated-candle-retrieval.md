- Linked spec: `docs/specs/06-local-aggregated-candle-retrieval.md`
- Replaced the backend `/api/candles` Jesse runtime path with a local candle aggregation service in `backend/app/services/candles.py`.
- Updated the route contract to require `exchange`, `symbol`, and `timeframe`, preserve millisecond timestamps, and allow `id: null` for synthesized candles.
- Added backend route and service tests covering 1m source-row loading, higher-timeframe aggregation, limit trimming, and incomplete-bucket handling.

- [x] AC1: `GET /api/candles` retrieves source rows from stored 1m candles and synthesizes supported higher timeframes locally instead of calling Jesse at runtime.
- [x] AC2: The backend uses UTC epoch-aligned bucket aggregation for supported timeframes, trims the normalized response to the requested `limit`, preserves newest-first ordering, and drops incomplete higher-timeframe buckets.
- [x] AC3: The API response remains compatible with the existing frontend contract for `exchange`, `symbol`, `timeframe`, OHLCV fields, and millisecond timestamps, and the implementation keeps `id` optional for synthesized candles.

- Validation run:
  - `make lint`
  - `make test`

- Open risks:
  - Large `limit` values on very large timeframes may still require loading many 1m rows and could need follow-up optimization if that becomes a hot path.
