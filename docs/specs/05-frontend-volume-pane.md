# Frontend Volume Pane

**Spec slug:** frontend-volume-pane
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-19

## Problem statement
- The current chart only renders price candles, even though each candle row already includes volume.
- This matters because volume is one of the most useful companion studies for price action, and Lightweight Charts supports multi-pane chart layouts out of the box.

## Scope
In scope:
- Add a dedicated volume pane below the existing candlestick pane.
- Render volume as a histogram series using the same candle dataset already passed to the chart.
- Color each volume bar according to whether the candle closed up or down.
- Add test coverage for the chart setup so the new pane wiring does not silently regress.

Out of scope / non-goals:
- Volume moving averages or other derived studies.
- User-configurable pane layouts.
- Additional indicators beyond raw volume.

## Assumptions
- Candle rows passed into the chart already contain `open`, `close`, and `volume`.
- The existing chart still uses Lightweight Charts and should remain visually consistent.
- A fixed-height secondary pane is acceptable for the first volume implementation.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `frontend/src/components/CandleChart.jsx`
  - `frontend/src/components/CandleChart.test.jsx`
  - `frontend/src/styles.css`
  - `docs/test-plans/05-frontend-volume-pane.md`
  - `.ai/pr-description/05-frontend-volume-pane.md`

### Inputs / outputs
- Inputs:
  - Chart-ready candle rows with `time`, `open`, `high`, `low`, `close`
  - Original candle volume values from the API response
- Outputs:
  - A candlestick pane for price
  - A lower histogram pane for volume
- Error handling:
  - Existing chart render error handling should remain in place if the chart library setup fails.

### Examples
```text
price pane:
- candlesticks for the selected exchange / symbol / timeframe

volume pane:
- green-ish histogram bars when close >= open
- red-ish histogram bars when close < open
```

## Acceptance criteria
- AC1: The chart renders volume in a separate lower pane using a histogram series rather than overlaying it on the price pane.
- AC2: Volume bars are derived from the displayed candle set and colored by candle direction.
- AC3: The chart component has automated test coverage verifying the additional histogram series and pane setup.

## Edge cases
- Empty candle arrays should continue to show the existing “no valid candle series” message instead of trying to create panes.
- Chart library initialization failures should still surface the existing inline error message.
- Volume bars should line up with the same `time` values used for the displayed candles.

## Test guidance
- AC1 -> component test asserting the histogram series is created in a separate pane
- AC2 -> component test asserting volume series data uses candle volume and up/down color logic
- AC3 -> passing frontend test run including the new chart component test

## Decision log
- 2026-03-19: Chose a separate pane instead of a volume overlay so price and volume remain visually distinct and the implementation follows the library’s pane examples directly.
