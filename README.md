# woody

`woody` is a full-stack candlestick chart application.

It includes:

- A FastAPI backend that serves candle data from PostgreSQL
- Local aggregation of higher timeframes from stored `1m` candles
- A React + Vite frontend for selecting exchange, symbol, and timeframe
- Lightweight Charts rendering for price candles and volume
- A spec-first workflow for changes in `docs/specs/`

## What The App Does

The frontend loads available candle series from `/api/candles/series`, defaults to the newest
series, and then requests chart data from `/api/candles`.

Supported chart flows currently include:

- selecting an exchange
- selecting a symbol
- selecting a timeframe
- rendering candlesticks with a separate volume pane

## Project Layout

```text
backend/
  alembic/
  app/
    api/
    core/
    db/
    models/
    services/
  tests/
frontend/
  src/
docs/
  specs/
  test-plans/
deploy/
docker-compose.yml
DEPLOY.md
```

## Local Setup

Create the root environment file:

```bash
cp .env.example .env
```

Set up Python dependencies:

```bash
make venv
make sync
```

Start PostgreSQL and run migrations:

```bash
make db-up
make migrate
```

Run the backend:

```bash
make backend-dev
```

In another terminal, run the frontend:

```bash
make frontend-dev
```

The backend API will be available at `http://localhost:8000/api`.
The frontend dev server will be available at `http://localhost:5173`.

The frontend reads `VITE_*` variables from the repo root `.env`.

## Common Commands

```bash
make lint
make test
make db-up
make db-down
make migrate
```

Frontend tests run separately:

```bash
cd frontend
npm test -- --run
```

## Workflow

This repository uses a spec-first process.

For code changes:

1. Update or add a spec in `docs/specs/<slug>.md`
2. Update or add the matching test plan in `docs/test-plans/<slug>.md`
3. Implement only the behavior described by the spec
4. Keep the PR draft in `.ai/pr-description/<slug>.md` aligned with the spec
5. Run `make lint` and `make test`

Acceptance criteria in specs must be labeled `AC1`, `AC2`, `AC3`, and so on.

## Production

Single-server deployment documentation lives in `DEPLOY.md`.

Deployment templates are included for:

- `deploy/nginx/woody.conf`
- `deploy/systemd/woody-backend.service`
