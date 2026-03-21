# Frontend Root Env Loading

**Spec slug:** frontend-root-env-loading
**Status:** Done
**Owner:** Codex
**Date:** 2026-03-18

## Problem statement
- After a reboot, the frontend dev server fell back to `http://localhost:8000/api` instead of using the configured LAN API URL from the repo root `.env`.
- This matters because developers expect one shared `.env` at the repo root to configure both backend and frontend local development.

## Scope
In scope:
- Make the Vite frontend read `VITE_*` variables from the repo root `.env`.
- Document the env-loading behavior in the local setup instructions.

Out of scope / non-goals:
- Changing the backend API default URL fallback in frontend source.
- Adding new frontend runtime configuration endpoints.

## Assumptions
- Developers start the frontend with `make frontend-dev` from the repository root.
- The repo root `.env` remains the intended local configuration file copied from `.env.example`.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `frontend/vite.config.js`
  - `README.md`

### Inputs / outputs
- Inputs:
  - Repo root `.env` values such as `VITE_API_BASE_URL`
- Outputs:
  - The Vite dev server exposes repo-root `VITE_*` values through `import.meta.env`
- Error handling:
  - If `VITE_API_BASE_URL` is absent, the frontend continues using its existing localhost fallback.

### Examples
```bash
cp .env.example .env
make frontend-dev
```

## Acceptance criteria
- AC1: Starting the frontend with `make frontend-dev` loads `VITE_*` variables from the repo root `.env`.
- AC2: If `VITE_API_BASE_URL` is defined in the repo root `.env`, the frontend uses that value instead of the localhost fallback.
- AC3: Setup documentation states that the frontend reads `VITE_*` values from the repo root `.env`.

## Edge cases
- Missing repo root `.env` should still allow the frontend to start and use code defaults.
- Non-`VITE_*` variables should not be exposed to the frontend runtime.

## Test guidance
- AC1 -> verify Vite config sets `envDir` to the repo root
- AC2 -> verify frontend API module still reads `import.meta.env.VITE_API_BASE_URL` first
- AC3 -> verify README quick-start notes where frontend env values are read from

## Decision log
- 2026-03-18: Chose Vite `envDir` over a tracked `frontend/.env` so the existing repo root `.env` remains the single local config file.
