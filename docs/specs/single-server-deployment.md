# Single Server Deployment

**Spec slug:** single-server-deployment
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-19

## Problem statement
- The application now has a working backend, frontend, and tests, but the repository does not yet provide a concrete production deployment path.
- This matters because shipping the app should not require reconstructing backend service setup, frontend static hosting, and reverse proxy routing from scratch.

## Scope
In scope:
- Document a single-server production deployment path for a Linux host.
- Provide configuration templates for a backend service and reverse proxy.
- Correct the environment example so it matches the current application defaults.
- Describe the production build, migration, and rollout steps for backend and frontend.

Out of scope / non-goals:
- Kubernetes or multi-node deployment.
- Managed cloud-specific Terraform or IaC.
- CI/CD pipeline automation.
- Containerizing the entire application stack.

## Assumptions
- The app is deployed to one Linux server with Python, Node, and a reverse proxy available.
- PostgreSQL is reachable from the server and Alembic migrations are run during deploy.
- The frontend is built to static assets and served separately from the FastAPI process.
- The backend continues to run as a Uvicorn process behind a reverse proxy.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `.env.example`
  - `README.md`
  - `DEPLOY.md`
  - `deploy/nginx/woody.conf`
  - `deploy/systemd/woody-backend.service`
  - `docs/test-plans/single-server-deployment.md`
  - `.ai/pr-description/single-server-deployment.md`

### Inputs / outputs
- Inputs:
  - Production `.env` values
  - Built frontend assets in `frontend/dist`
  - Migrated PostgreSQL database
- Outputs:
  - A documented deployment path for serving `/` from static frontend assets
  - A documented deployment path for proxying `/api` to FastAPI
  - A backend service unit and reverse proxy config template
- Error handling:
  - The deployment guide should include validation steps so the operator can confirm backend health, static frontend serving, and API proxying after rollout.

### Examples
```text
/
-> static files from frontend/dist

/api/*
-> proxied by nginx to 127.0.0.1:8000

systemd:
- starts Uvicorn for FastAPI
- restarts on failure
```

## Acceptance criteria
- AC1: The repository includes a deployment guide describing how to build the frontend, install backend dependencies, run Alembic migrations, and start the backend for production.
- AC2: The repository includes a reverse proxy config template that serves the frontend statically and proxies `/api` requests to the backend service.
- AC3: The repository includes a backend service template and an environment example consistent with the current application defaults, including the existing `jesse_db` database name.

## Edge cases
- Frontend routes should fall back to `index.html` so client-side navigation keeps working.
- Proxy configuration must preserve `/api` routing without rewriting the application prefix away.
- The example environment file should not reference removed Jesse-era defaults.

## Test guidance
- AC1 -> inspect `DEPLOY.md` and `README.md`
- AC2 -> inspect `deploy/nginx/woody.conf`
- AC3 -> inspect `deploy/systemd/woody-backend.service` and `.env.example`

## Decision log
- 2026-03-19: Chose a single-server deployment path first because it is the smallest useful production target for the current app shape.
- 2026-03-19: Chose a reverse-proxy plus Uvicorn service layout so the frontend can be served statically while the backend remains a small FastAPI process.
