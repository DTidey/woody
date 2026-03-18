# Frontend Selectable Candle Series

**Spec slug:** frontend-selectable-candle-series
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-18

## Problem statement
- The frontend currently fetches the latest candles without choosing a symbol or timeframe first.
- This matters because candlestick charts should render one coherent series, and mixed series responses increase the chance of invalid chart input and confusing UI state.
- The candle table also stores `exchange`, so treating only `symbol` and `timeframe` as a series identifier can still blend distinct feeds into one chart request.

## Scope
In scope:
- Expose available candle exchange/symbol/timeframe options from the backend.
- Let the frontend choose an exchange, symbol, and timeframe before fetching chart candles.
- Default the frontend to the newest available series.
- Show a compact debug view of the sanitized candle rows being passed into the chart.
- Keep the backend series-options lookup fast enough for initial page load as candle history grows.

Out of scope / non-goals:
- Multi-series overlays on one chart.
- Persisting the selected series across browser sessions.
- Adding pagination or infinite scrolling to candles.

## Assumptions
- The newest available candle series is a reasonable default for first render.
- The backend database may contain multiple symbols and timeframes at once.
- A candlestick chart should render one symbol/timeframe pair at a time.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `backend/app/api/routes/candles.py`
  - `backend/tests/test_candles_route.py`
  - `frontend/src/App.jsx`
  - `frontend/src/lib/api.js`
  - `frontend/src/lib/candles.js`
  - `frontend/src/styles.css`

### Inputs / outputs
- Inputs:
  - Available candle rows in the database
  - User-selected `exchange`, `symbol`, and `timeframe`
- Outputs:
  - A backend response listing available series options
  - A frontend UI that fetches and charts candles for the selected exchange/symbol/timeframe only
  - A frontend debug panel showing the selected series and a sample of the chart input rows
- Error handling:
  - If no series options exist, the frontend should show an empty-state message and avoid candle fetches.
  - If a fetch fails, the existing inline API error state should continue to render.

### Examples
```text
GET /api/candles/series
-> [
     { "exchange": "binance", "symbol": "BTC-USDT", "timeframe": "1h" },
     { "exchange": "coinbase", "symbol": "ETH-USD", "timeframe": "4h" }
   ]

GET /api/candles?exchange=binance&symbol=BTC-USDT&timeframe=1h&limit=200
-> 200 binance BTC-USDT 1h candle rows
```

## Acceptance criteria
- AC1: The backend exposes an endpoint that returns distinct available candle series as `exchange`/`symbol`/`timeframe` tuples ordered so the newest series appears first.
- AC2: On load, the frontend requests available series, defaults to the first returned series, and fetches candles only for that selected `exchange`, `symbol`, and `timeframe`.
- AC3: The frontend renders exchange, symbol, and timeframe selectors that refetch candles when the selected series changes, shows a clear empty state when no series options exist, and displays a debug sample of the candle rows passed to the chart.

## Edge cases
- Duplicate rows for the same exchange/symbol/timeframe should appear once in the series-options response.
- A symbol may exist with multiple timeframes on one exchange.
- The same symbol/timeframe may exist on multiple exchanges and must remain selectable as separate series.
- No available candle rows should not trigger a candle fetch with missing filters.

## Test guidance
- AC1 -> backend route test for distinct ordered series tuples
- AC2 -> frontend data-flow inspection verifying candle fetches include selected exchange/symbol/timeframe
- AC3 -> frontend UI inspection verifying selectors, empty-state behavior, and the chart-input debug panel

## Performance notes
- The backend series-options lookup should avoid scanning every candle row to discover the latest entry for each series.
- Query optimization must preserve the existing response shape and ordering expected by AC1.

## Decision log
- 2026-03-18: Chose a dedicated series-options endpoint instead of deriving options from a mixed candle fetch so the chart request can stay scoped to one series from the start.
- 2026-03-18: Added an on-screen debug sample so chart-input issues can be inspected without opening browser devtools.
- 2026-03-18: Expanded series identity to include `exchange` so chart requests do not blend candles from different venues.
- 2026-03-18: Replaced the index-first optimization attempt with an index-jumping latest-series query after profiling showed the original `DISTINCT ON` path still walked the full candle index.
- 2026-03-18: On the live post-drop database, the original `DISTINCT ON` query still timed out past 15 seconds while the index-jumping replacement completed in about 112 milliseconds.
