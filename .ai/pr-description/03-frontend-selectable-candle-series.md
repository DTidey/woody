## Summary
- Replaced the backend `/api/candles/series` lookup with an index-jumping recursive query in `backend/app/api/routes/candles.py`.
- Preserved the existing series endpoint contract while simplifying the frontend to a cleaner `woody` chart view.
- Removed the API/debug stats chrome, sorted symbol options ascending, and exposed supported higher timeframes in the selector.
- Added a follow-up Alembic migration to drop `candle_series_lookup_idx` cleanly on databases that already applied the earlier migration.
- Documented the live profiling result showing the old `DISTINCT ON` query timing out past 15 seconds after the index drop while the replacement query completed in about 112 ms.

## Spec
- `docs/specs/03-frontend-selectable-candle-series.md`

## Acceptance Criteria
- [x] AC1: The backend exposes an endpoint that returns distinct available candle series as `exchange`/`symbol`/`timeframe` tuples ordered so the newest series appears first.
- [x] AC2: On load, the frontend requests available series, defaults to the first returned series, and fetches candles only for that selected `exchange`, `symbol`, and `timeframe`.
- [x] AC3: The frontend renders a simplified `woody` interface that removes the API/debug stats, sorts symbol options ascending, offers supported higher timeframes in the timeframe selector, refetches candles when the selected series changes, and shows a clear empty state when no series options exist.

## Validation
- [x] `make lint`
- [x] `make test`

## Open Risks
- The live database should run the new drop migration so environments that previously created `candle_series_lookup_idx` converge on the intended schema.
