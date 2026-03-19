# Frontend Volume Pane

## Summary
- Added a lower volume pane to the candlestick chart.
- Rendered volume as a histogram series aligned to the displayed candle times.
- Added chart component tests by mocking Lightweight Charts.

## Acceptance criteria coverage
- AC1: Inspect `frontend/src/components/CandleChart.jsx` and `frontend/src/components/CandleChart.test.jsx` to confirm the histogram series is created in pane index `1`.
- AC2: Inspect `frontend/src/components/CandleChart.jsx` and `frontend/src/components/CandleChart.test.jsx` to confirm volume values come from the candle rows and colors follow candle direction.
- AC3: Run `cd frontend && npm test -- --run` and confirm the new chart test passes.

## Validation run
- `cd frontend && npm test -- --run`
- `make lint`
- `make test`

## Risks
- The current pane height is fixed in code, so later UI tuning may still be useful after seeing it with larger datasets.
