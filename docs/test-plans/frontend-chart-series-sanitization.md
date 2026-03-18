# Test Plan: frontend-chart-series-sanitization

## What changed
- Added a frontend candle sanitization helper to build one valid candlestick series.
- Updated the chart component to render inline errors instead of failing hard.
- Added a small UI note when rows are dropped before rendering.

## Acceptance criteria coverage
- AC1: Inspect `frontend/src/lib/candles.js` and `frontend/src/App.jsx` to confirm the newest row's symbol/timeframe defines the rendered series.
- AC2: Inspect `frontend/src/lib/candles.js` to confirm invalid OHLC/timestamp rows are skipped and duplicate timestamps are deduplicated.
- AC3: Inspect `frontend/src/components/CandleChart.jsx` to confirm chart exceptions are caught and rendered as a visible message.

## Edge cases
- Empty datasets render the fallback message.
- Extremely large timestamps normalize down to seconds.
- Mixed symbol/timeframe datasets do not get passed straight into the chart library.

## Notes
- Automated frontend tests are not yet present in this scaffold, so validation is via linting plus manual dev-server verification.
- A good follow-up is adding a small unit test harness for `frontend/src/lib/candles.js`.
