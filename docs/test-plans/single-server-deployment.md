# Single Server Deployment

## Summary
- Added a concrete single-server production deployment guide.
- Added an nginx config template for static frontend hosting plus `/api` proxying.
- Added a systemd service template for the FastAPI backend.
- Corrected the example environment file to match current app defaults.

## Acceptance criteria coverage
- AC1: Inspect `DEPLOY.md` and `README.md` to confirm the guide covers install, sync, build, migrate, and service startup steps.
- AC2: Inspect `deploy/nginx/woody.conf` to confirm `/` serves frontend assets and `/api/` proxies to `127.0.0.1:8000`.
- AC3: Inspect `deploy/systemd/woody-backend.service` and `.env.example` to confirm the backend service template and example environment match the current application defaults.

## Validation run
- `make lint`
- `make test`
- `cd frontend && npm test -- --run`

## Risks
- The deployment templates are intentionally generic and still need site-specific values such as domain name, filesystem paths, and production secrets.
