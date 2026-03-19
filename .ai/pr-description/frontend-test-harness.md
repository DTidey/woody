- Linked spec: `docs/specs/frontend-test-harness.md`
- Added a lightweight frontend test harness using Vitest, jsdom, and Testing Library.
- Added unit tests for candle sanitization behavior and component tests for `App.jsx` selector/data-flow behavior with the chart mocked.
- Added a frontend package test script for local test runs.

- [x] AC1: The frontend has a working Vitest + jsdom test harness with a package script that runs tests locally.
- [x] AC2: `frontend/src/lib/candles.js` has unit tests covering valid-series selection, invalid-row dropping, duplicate timestamp handling, and timestamp normalization.
- [x] AC3: `frontend/src/App.jsx` has component tests covering default selection, ascending symbol ordering, supported higher-timeframe options, and empty/error states with the chart component mocked.

- Validation run:
  - `cd frontend && npm test -- --run`
  - `make lint`
  - `make test`

- Open risks:
  - The tests intentionally mock the chart component, so chart-library integration regressions are still outside this harness.
