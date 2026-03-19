# woody

Full-stack application scaffold with:

- FastAPI for the backend API
- SQLAlchemy for ORM models
- Alembic for database migrations
- psycopg for PostgreSQL connectivity
- React + Vite for the frontend

## Project Layout

```text
backend/
  app/
  alembic/
  tests/
frontend/
docs/
docker-compose.yml
```

## Quick Start

```bash
cp .env.example .env
make venv
make compile
make sync
make db-up
make backend-dev
```

In another terminal:

```bash
make frontend-dev
```

The frontend dev server reads `VITE_*` variables from the repo root `.env`.

The backend API will be available at `http://localhost:8000/api`, and the frontend dev server
will run at `http://localhost:5173`.

## Common Commands

```bash
make lint
make test
make migrate
make db-down
```

## Production

A single-server deployment path is documented in:

```text
DEPLOY.md
```

The repository also includes deployment templates for:

- `deploy/nginx/woody.conf`
- `deploy/systemd/woody-backend.service`

## Next Recommended Steps

1. Replace the example SQLAlchemy model with your real domain models.
2. Generate your first Alembic migration from `backend/`.
3. Add API routes that read from PostgreSQL.
4. Connect React screens to those routes.
