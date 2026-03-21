# Frontend Test Harness

**Spec slug:** frontend-test-harness
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-19

## Problem statement
- The frontend now contains real UI state and candle-shaping behavior, but the repo has no frontend test harness.
- This matters because selector defaults, timeframe options, empty/error states, and chart-input sanitization are easy to regress and currently require manual browser checks.

## Scope
In scope:
- Add a lightweight frontend test harness for the Vite React app.
- Add unit tests for candle sanitization behavior in `frontend/src/lib/candles.js`.
- Add component tests for `frontend/src/App.jsx` with API calls and chart rendering mocked.
- Expose a frontend test command through `frontend/package.json`.

Out of scope / non-goals:
- Visual regression testing.
- End-to-end browser automation.
- Deep chart-library integration tests.

## Assumptions
- The highest-value frontend tests are behavior-focused and do not need to render `lightweight-charts`.
- Mocking the chart component is acceptable for `App.jsx` tests.
- A jsdom-based harness is sufficient for the current frontend surface area.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `frontend/package.json`
  - `frontend/vite.config.js`
  - `frontend/src/App.jsx`
  - `frontend/src/lib/candles.js`
  - `frontend/src/test/setup.js`
  - `frontend/src/**/*.test.jsx`
  - `frontend/src/**/*.test.js`
  - `docs/test-plans/04-frontend-test-harness.md`
  - `.ai/pr-description/04-frontend-test-harness.md`

### Inputs / outputs
- Inputs:
  - Candle rows returned by mocked API responses
  - User selections in the `App` exchange/symbol/timeframe controls
- Outputs:
  - Passing frontend unit and component tests
  - A repeatable `npm test` command in `frontend/`
- Error handling:
  - Tests should mock network responses rather than relying on live backend availability.
  - The harness should fail fast in CI or local runs when UI behavior regresses.

### Examples
```text
cd frontend
npm test -- --run

tests:
- buildChartSeries drops invalid rows and deduplicates timestamps
- App defaults to a valid series and fetches candles for the selected exchange/symbol/timeframe
- App shows empty and error states clearly
```

## Acceptance criteria
- AC1: The frontend has a working Vitest + jsdom test harness with a package script that runs tests locally.
- AC2: `frontend/src/lib/candles.js` has unit tests covering valid-series selection, invalid-row dropping, duplicate timestamp handling, and timestamp normalization.
- AC3: `frontend/src/App.jsx` has component tests covering default selection, ascending symbol ordering, supported higher-timeframe options, and empty/error states with the chart component mocked.

## Edge cases
- The first backend series option may not be alphabetically first, so symbol ordering should still be asserted separately.
- Timeframe options should include higher intervals even when the series endpoint only reports stored DB series identities.
- Empty series responses should not trigger candle fetches.
- API errors should surface user-facing messages instead of silently failing.

## Test guidance
- AC1 -> `frontend/package.json` and `frontend/vite.config.js` inspection plus a passing frontend test run
- AC2 -> `frontend/src/lib/candles.test.js`
- AC3 -> `frontend/src/App.test.jsx`

## Decision log
- 2026-03-19: Chose Vitest with jsdom and Testing Library because it fits the existing Vite React stack with minimal setup.
- 2026-03-19: Chose to mock the chart component so tests focus on frontend state and data-flow behavior rather than chart-library internals.
