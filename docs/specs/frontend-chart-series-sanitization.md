# Frontend Chart Series Sanitization

**Spec slug:** frontend-chart-series-sanitization
**Status:** Done
**Owner:** Codex
**Date:** 2026-03-18

## Problem statement
- The frontend successfully fetches candles, but the page can go black when the chart library receives rows that do not form one valid candlestick series.
- This matters because the backend may return mixed symbols, mixed timeframes, duplicate timestamps, or malformed rows within the latest global candle window.

## Scope
In scope:
- Sanitize fetched candle rows into one chartable candlestick series before rendering.
- Surface chart-render failures in the UI instead of crashing the screen.
- Inform the user when rows were dropped before charting.

Out of scope / non-goals:
- Adding UI controls for symbol or timeframe selection.
- Changing the backend candle query behavior.

## Assumptions
- The newest returned candle defines the primary symbol and timeframe to chart.
- A candlestick chart should only render one consistent symbol/timeframe series at a time.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `frontend/src/App.jsx`
  - `frontend/src/components/CandleChart.jsx`
  - `frontend/src/lib/candles.js`
  - `frontend/src/styles.css`

### Inputs / outputs
- Inputs:
  - Candle rows returned by `GET /api/candles`
- Outputs:
  - A single sanitized candlestick series rendered in the frontend
  - A UI note when rows are filtered or dropped
  - A visible error panel if chart rendering still fails
- Error handling:
  - Rows with invalid timestamps or OHLC values are skipped.
  - Duplicate timestamps are deduplicated by timestamp.
  - Chart exceptions are shown as an inline panel message.

### Examples
```text
API rows: latest 200 rows across multiple symbols/timeframes
Frontend chart: rows matching the newest row's symbol/timeframe, deduplicated and sorted
```

## Acceptance criteria
- AC1: The frontend derives one chartable series from the fetched rows by keeping the newest row's symbol/timeframe and dropping rows outside that series.
- AC2: The frontend skips invalid candle rows and deduplicates duplicate timestamps before calling the chart library.
- AC3: If chart rendering still throws, the UI shows an inline error message instead of a blank screen.

## Edge cases
- Empty responses should show no chart data rather than crashing.
- Millisecond, microsecond, and nanosecond timestamps should normalize to seconds.
- Mixed-symbol or mixed-timeframe responses should still render one stable chart.

## Test guidance
- AC1 -> verify the sanitization helper selects the newest symbol/timeframe pair
- AC2 -> verify sanitization drops malformed rows and duplicate timestamps
- AC3 -> verify the chart component catches render errors and shows a message

## Decision log
- 2026-03-18: Chose frontend sanitization first so the UI remains robust even if the backend continues returning mixed candle rows.
