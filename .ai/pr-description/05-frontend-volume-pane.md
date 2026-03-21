- Linked spec: `docs/specs/05-frontend-volume-pane.md`
- Added a lower volume pane to the Lightweight Charts chart using a histogram series.
- Colored volume bars by candle direction and aligned them to the displayed candle times.
- Added chart component tests with a mocked chart API to cover the new pane wiring.

- [x] AC1: The chart renders volume in a separate lower pane using a histogram series rather than overlaying it on the price pane.
- [x] AC2: Volume bars are derived from the displayed candle set and colored by candle direction.
- [x] AC3: The chart component has automated test coverage verifying the additional histogram series and pane setup.

- Validation run:
  - `cd frontend && npm test -- --run`
  - `make lint`
  - `make test`

- Open risks:
  - The pane height is currently fixed and may still need visual tuning with real production datasets.
