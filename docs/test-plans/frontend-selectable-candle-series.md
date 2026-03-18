# Test Plan: frontend-selectable-candle-series

## What changed
- Added a backend endpoint for available candle series options.
- Updated the frontend to select an exchange/symbol/timeframe tuple before fetching candles.
- Added an empty state for installs with no available candle series.
- Added an on-screen debug panel for the sanitized candles passed to the chart.
- Reworked the backend series-options query to jump between distinct series keys instead of scanning all candle rows.

## Acceptance criteria coverage
- AC1: Add a backend test that verifies distinct exchange/symbol/timeframe tuples are returned newest-first from the new series-options endpoint.
- AC2: Inspect frontend query setup to confirm candles are fetched only after a selected series exists and that the selected `exchange`, `symbol`, and `timeframe` are passed to the API request.
- AC3: Inspect frontend UI to confirm exchange/symbol/timeframe selectors are rendered, an empty state appears when no series options are available, and a debug sample of chart-input candles is visible.

## Edge cases
- Duplicate DB rows for one exchange/symbol/timeframe do not create duplicate selector options.
- Symbols with multiple timeframes expose each valid pair on the selected exchange.
- The same symbol/timeframe on multiple exchanges remains selectable as separate series.
- Empty series-options responses skip candle fetching and show an explanatory message.

## Notes
- Current automated test coverage is strongest on the backend route behavior.
- The performance improvement is validated by preserving the existing route contract while changing the SQL path under it.
- Live profiling on 2026-03-18 showed the old `DISTINCT ON` series query timing out past 15 seconds after the index drop, while the replacement query completed in about 112 milliseconds on the same database.
- A good follow-up is adding frontend component tests once a JS test harness is introduced.
