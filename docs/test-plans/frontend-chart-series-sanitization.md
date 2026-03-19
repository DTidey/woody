# Test Plan: frontend-chart-series-sanitization

## What changed
- Added a frontend candle sanitization helper to build one valid candlestick series.
- Updated the chart component to render inline errors instead of failing hard.

## Acceptance criteria coverage
- AC1: Inspect `frontend/src/lib/candles.js` and `frontend/src/App.jsx` to confirm the newest row's symbol/timeframe defines the rendered series.
- AC2: Inspect `frontend/src/lib/candles.js` to confirm invalid OHLC/timestamp rows are skipped and duplicate timestamps are deduplicated.
- AC3: Inspect `frontend/src/components/CandleChart.jsx` to confirm chart exceptions are caught and rendered as a visible message.

## Edge cases
- Empty datasets render the fallback message.
- Extremely large timestamps normalize down to seconds.
- Mixed symbol/timeframe datasets do not get passed straight into the chart library.

## Notes
- Automated frontend coverage now exists through the Vitest harness, including sanitization tests in `frontend/src/lib/candles.test.js`.
