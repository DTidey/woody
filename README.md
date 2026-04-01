# woody

`woody` is a full-stack candlestick chart application.

It includes:

- A FastAPI backend that serves candle data from PostgreSQL
- Local aggregation of higher timeframes from stored `1m` candles
- A React + Vite frontend for selecting exchange, symbol, and timeframe
- Lightweight Charts rendering for price candles and volume
- A spec-first workflow for changes in `docs/specs/`

Project history uses two parallel conventions:
- Numbered spec packets like `docs/specs/09-release-changelog-policy.md` track implementation order.
- Release versions in `CHANGELOG.md` use `MAJOR.MINOR.PATCH` formatting and are created only on explicit request.

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

For a step-by-step Ubuntu 22.04 setup guide, see
[`docs/setup-ubuntu-22.04.md`](docs/setup-ubuntu-22.04.md).

Create the root environment file:

```bash
cp .env.example .env
```

Set up Python dependencies:

```bash
make venv PYTHON=python3.12
make sync
```

On Ubuntu 22.04, prefer `PYTHON=python3.12` so the virtualenv matches the pinned dependency set in this repo.

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
make security
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

1. Update or add a spec in `docs/specs/<nn>-<slug>.md`
2. Update or add the matching test plan in `docs/test-plans/<nn>-<slug>.md`
3. Implement only the behavior described by the spec
4. Keep the PR draft in `.ai/pr-description/<nn>-<slug>.md` aligned with the spec
5. Run `make lint`, `make test`, and `make security`

Use the next available two-digit prefix such as `03-frontend-selectable-candle-series.md`, and keep that number stable once it exists.

Acceptance criteria in specs must be labeled `AC1`, `AC2`, `AC3`, and so on.

## GitHub Enforcement

- Protect `main` in GitHub with branch protection or a repository ruleset.
- Require a pull request before merging into `main`.
- Require these exact status checks before merging:
  - `CI / test`
  - `CodeQL / analyze`
- Dismiss stale approvals when new commits are pushed.
- Block force pushes and branch deletion on `main`.
- Keep `.github/CODEOWNERS` enabled so review ownership stays explicit.
- Let Dependabot manage weekly updates for `pip` and GitHub Actions dependencies.

## Security Review

- Code-changing specs should include a `Security considerations` section so authors can call out auth/authz, input handling, secrets, data exposure, file access, network access, and dependency impact.
- PR materials should summarize the security review disposition so reviewers know whether there is no meaningful security impact or a sensitive area that needs extra scrutiny.
- This repository currently uses `make security` as the default automation entry point, backed by Bandit and pip-audit.
- The default `pip-audit` invocation currently ignores `CVE-2026-4539` for `pygments` because no fixed version was available when this workflow was added; revisit that exception when upstream guidance changes.

## Releases

Release notes live in `CHANGELOG.md`.

- Keep ongoing changes under `Unreleased`.
- Cut a versioned section like `0.1.0` only when you explicitly want to create a release.
- Treat numbered spec packets and release versions as separate concepts.

## Production

Single-server deployment documentation lives in `DEPLOY.md`.

Deployment templates are included for:

- `deploy/nginx/woody.conf`
- `deploy/systemd/woody-backend.service`
