## Summary
- Replaced the backend `/api/candles/series` lookup with an index-jumping recursive query in `backend/app/api/routes/candles.py`.
- Preserved the existing series endpoint contract and frontend behavior while removing the need for the extra `candle_series_lookup_idx`.
- Added a follow-up Alembic migration to drop `candle_series_lookup_idx` cleanly on databases that already applied the earlier migration.
- Documented the live profiling result showing the old `DISTINCT ON` query timing out past 15 seconds after the index drop while the replacement query completed in about 112 ms.

## Spec
- `docs/specs/frontend-selectable-candle-series.md`

## Acceptance Criteria
- [x] AC1: The backend exposes an endpoint that returns distinct available candle series as `exchange`/`symbol`/`timeframe` tuples ordered so the newest series appears first.
- [x] AC2: On load, the frontend requests available series, defaults to the first returned series, and fetches candles only for that selected `exchange`, `symbol`, and `timeframe`.
- [x] AC3: The frontend renders exchange, symbol, and timeframe selectors that refetch candles when the selected series changes, shows a clear empty state when no series options exist, and displays a debug sample of the candle rows passed to the chart.

## Validation
- [x] `make lint`
- [x] `make test`

## Open Risks
- The live database should run the new drop migration so environments that previously created `candle_series_lookup_idx` converge on the intended schema.
