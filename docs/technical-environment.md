# Technical Environment

This document summarizes the technical environment for `woody` and is written to be reused as a model for similar full-stack projects.

## 1. Application summary

`woody` is a full-stack candlestick chart application with:

- a FastAPI backend that exposes `/api` endpoints
- a React and Vite frontend that renders chart data in the browser
- a PostgreSQL database that stores candle data
- a simple deployment model built around nginx, systemd, and a single application server

At a high level, the frontend requests candle metadata and chart data from the backend, and the backend reads from PostgreSQL using SQLAlchemy and returns JSON responses for the chart UI.

## 2. Architecture and service boundaries

### Backend

- Runtime: Python 3.12 is the preferred local and deployment runtime in repository docs.
- Framework: FastAPI
- ASGI server: Uvicorn with standard extras
- Data access: SQLAlchemy 2.x ORM and SQL execution
- Database driver: `psycopg` 3
- Configuration: `pydantic-settings` loading values from the repo root `.env`
- Migrations: Alembic

Backend code lives under `backend/app/` with this rough split:

- `api/` for HTTP routes
- `services/` for domain logic such as candle retrieval and aggregation
- `db/` for session and engine setup
- `models/` for SQLAlchemy models
- `core/` for settings and shared backend configuration

### Frontend

- Runtime: Node.js 20+ in deployment docs
- Framework: React 18
- Build tool and dev server: Vite 5
- Data fetching and cache layer: TanStack React Query 5
- Charting library: Lightweight Charts 5
- Test runner: Vitest with Testing Library and JSDOM

Frontend code lives under `frontend/src/` with this rough split:

- `components/` for UI pieces such as the candle chart
- `lib/` for API and data helpers
- `App.jsx` as the main application shell

### Database and supporting services

- Database engine: PostgreSQL 16 in local Docker Compose
- Local container orchestration: `docker compose`
- Persistent local storage: named Docker volume `postgres_data`

### Production topology

The documented production model is a single server with:

- nginx serving the built frontend from `frontend/dist`
- nginx proxying `/api/*` requests to the backend on `127.0.0.1:8000`
- systemd managing the backend process
- PostgreSQL running as the application data store

## 3. Runtime versions and key dependencies

### Python environment

- Preferred interpreter: Python 3.12
- Ruff target version in [`pyproject.toml`](/home/david/woody/pyproject.toml): Python 3.11
- Main backend packages pinned in [`requirements.txt`](/home/david/woody/requirements.txt):
  - `fastapi==0.135.1`
  - `uvicorn[standard]==0.42.0`
  - `sqlalchemy==2.0.48`
  - `alembic==1.18.4`
  - `psycopg[binary]==3.3.3`
  - `pydantic-settings==2.13.1`

### JavaScript environment

- Node.js target in deployment docs: Node.js 20+
- Main frontend packages pinned in [`frontend/package.json`](/home/david/woody/frontend/package.json):
  - `react@18.3.1`
  - `react-dom@18.3.1`
  - `@tanstack/react-query@5.90.5`
  - `lightweight-charts@5.0.9`
  - `vite@5.4.10`
  - `vitest@2.1.8`

### Infrastructure dependencies

- PostgreSQL container image in [`docker-compose.yml`](/home/david/woody/docker-compose.yml): `postgres:16`
- Reverse proxy in deployment docs: nginx
- Process manager in deployment docs: systemd

## 4. Configuration model

The backend settings class reads from the repo root `.env` file and ignores unknown values. The frontend also reads `VITE_*` variables from the same root `.env` during local development and build time.

### Current environment variables

Documented in [`.env.example`](/home/david/woody/.env.example):

| Variable | Used by | Purpose | Example |
| --- | --- | --- | --- |
| `APP_NAME` | Backend | FastAPI application title | `Woody API` |
| `API_PREFIX` | Backend | Route prefix for API endpoints | `/api` |
| `DATABASE_URL` | Backend | PostgreSQL SQLAlchemy connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/jesse_db` |
| `FRONTEND_ORIGIN` | Backend | Allowed browser origin for CORS | `http://localhost:5173` |
| `VITE_API_BASE_URL` | Frontend | Base URL used by the browser app to call the API | `http://localhost:8000/api` |

### Configuration notes

- Backend defaults exist in code, but the intended source of truth is the root `.env`.
- `FRONTEND_ORIGIN` affects backend CORS behavior and requires a backend restart when changed.
- `VITE_API_BASE_URL` is baked into the frontend build output and requires a frontend rebuild when changed.
- For production behind nginx, the deployment guide recommends `VITE_API_BASE_URL=/api` to keep API requests same-origin.

## 5. Local development environment

### Core setup flow

1. Create the root environment file: `cp .env.example .env`
2. Create a virtual environment: `make venv PYTHON=python3.12`
3. Install Python dependencies: `make sync`
4. Start PostgreSQL: `make db-up`
5. Run database migrations: `make migrate`
6. Start the backend: `make backend-dev`
7. Start the frontend in a separate terminal: `make frontend-dev`

### Local service endpoints

- Backend API: `http://localhost:8000/api`
- Frontend dev server: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

### Local workflow characteristics

- Backend runs with Uvicorn reload enabled for development.
- Frontend development runs through the Vite dev server.
- The frontend install step currently happens inside `make frontend-dev` via `npm install`.
- Database lifecycle for local work is intentionally lightweight and Docker-based.

## 6. Quality, testing, and validation toolchain

### Required repository commands

From [`Makefile`](/home/david/woody/Makefile):

- `make lint`
- `make test`

### What they do

- `make lint` runs `ruff check .` and `ruff format --check .`
- `make test` runs backend pytest suites with `PYTHONPATH=backend`
- Frontend tests are run separately with `cd frontend && npm test -- --run`

### Test stack

- Backend tests: `pytest`
- Backend HTTP/client utilities available in dev dependencies: `httpx`
- Frontend tests: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, and `jsdom`
- Git hook tooling: `pre-commit`

## 7. Deployment environment

The repository’s documented deployment target is a single Linux server, with Ubuntu 22.04 called out explicitly in the setup and deployment docs.

### Production flow

1. Clone the repository onto the server.
2. Create the root `.env`.
3. Build the Python virtualenv and sync dependencies.
4. Run Alembic migrations.
5. Build the frontend into `frontend/dist`.
6. Run the backend through a systemd service.
7. Serve static frontend assets and reverse proxy the API through nginx.

### Production characteristics

- Backend bind address: `127.0.0.1:8000`
- Frontend delivery: static files from `frontend/dist`
- API exposure: nginx reverse proxy on `/api/`
- Process supervision: systemd
- Data store: PostgreSQL

### Operational notes

- Frontend and backend configuration have different reload needs.
- The deployment docs distinguish deploy/admin responsibilities from the low-privilege service user that runs the backend.
- File permissions matter because both the backend service user and nginx need access to different parts of the repository tree.

## 8. Repo conventions that shape the environment

- The project follows a spec-first workflow, with specs stored in `docs/specs/`.
- Code-changing work is expected to carry a matching test plan in `docs/test-plans/`.
- Local automation is centralized in `Makefile` targets instead of scattered shell scripts.
- Python dependencies are managed through `pip-tools`-generated lock files.
- Frontend and backend are developed from one repository and share the same root `.env` file.

## 9. Reusable template for similar projects

For a similar application, this document structure is a good starting point:

1. Application summary
2. Architecture and service boundaries
3. Runtime versions and key dependencies
4. Configuration model and environment variables
5. Local development workflow
6. Quality and validation commands
7. Deployment topology
8. Operational notes and known constraints

When adapting this for another project, keep these prompts:

- What are the frontend, backend, database, queue, and proxy layers?
- Which runtimes and package managers are pinned, and where are they declared?
- Which environment variables are required, and which side consumes each one?
- What commands must a new developer run to start the stack locally?
- What commands must pass before merge?
- How does production differ from local development?
- Which pieces are single-node assumptions that may need to change later?

## 10. Woody-specific gaps and follow-up opportunities

This document reflects the current repository state. If you want an even stronger reusable template later, the next worthwhile additions would be:

- a standard "technical environment template" file with placeholder fields only
- a diagram of request flow between browser, nginx, backend, and PostgreSQL
- a short runbook for secrets handling, backups, and monitoring
