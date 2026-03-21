# Test Plan: frontend-selectable-candle-series

## What changed
- Added a backend endpoint for available candle series options.
- Updated the frontend to select an exchange/symbol/timeframe tuple before fetching candles.
- Added an empty state for installs with no available candle series.
- Simplified the frontend copy and removed API/debug status panels once the candle flow was stable.
- Sorted symbol options ascending and exposed supported higher timeframes in the selector.
- Reworked the backend series-options query to jump between distinct series keys instead of scanning all candle rows.

## Acceptance criteria coverage
- AC1: Add a backend test that verifies distinct exchange/symbol/timeframe tuples are returned newest-first from the new series-options endpoint.
- AC2: Inspect frontend query setup to confirm candles are fetched only after a selected series exists and that the selected `exchange`, `symbol`, and `timeframe` are passed to the API request.
- AC3: Inspect frontend UI to confirm the page is branded as `woody`, the API/debug stats are removed, symbol options are sorted ascending, supported higher timeframes are selectable, and an empty state appears when no series options are available.

## Edge cases
- Duplicate DB rows for one exchange/symbol/timeframe do not create duplicate selector options.
- Symbols are sorted alphabetically regardless of recency order in the backend series response.
- Symbols with stored 1m history can request higher-timeframe chart candles through the selector even when those timeframes are not stored directly in the DB.
- The same symbol/timeframe on multiple exchanges remains selectable as separate series.
- Empty series-options responses skip candle fetching and show an explanatory message.

## Notes
- Automated coverage now exists for the frontend selector/data-flow behavior through the Vitest harness, though the backend route behavior remains more fully exercised.
- The performance improvement is validated by preserving the existing route contract while changing the SQL path under it.
- Live profiling on 2026-03-18 showed the old `DISTINCT ON` series query timing out past 15 seconds after the index drop, while the replacement query completed in about 112 milliseconds on the same database.
