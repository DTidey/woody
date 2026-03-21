# Frontend Test Harness

## Summary
- Added a minimal frontend test harness using Vitest, jsdom, and Testing Library.
- Covered candle sanitization logic with unit tests.
- Covered `App.jsx` data flow and selector behavior with mocked component tests.

## Acceptance criteria coverage
- AC1: Inspect `frontend/package.json`, `frontend/vite.config.js`, and `frontend/src/test/setup.js` to confirm the frontend has a working test harness and package script.
- AC2: Inspect `frontend/src/lib/candles.test.js` to confirm candle sanitization tests cover invalid rows, duplicate timestamps, and timestamp normalization.
- AC3: Inspect `frontend/src/App.test.jsx` to confirm component tests cover default selection, ascending symbol ordering, supported higher-timeframe options, and empty/error states.

## Validation run
- `cd frontend && npm test -- --run`
- `make lint`
- `make test`

## Risks
- The harness intentionally mocks chart rendering, so regressions inside `lightweight-charts` integration are still outside automated coverage.
