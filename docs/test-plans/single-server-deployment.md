# Single Server Deployment

## Summary
- Added a concrete single-server production deployment guide.
- Added an nginx config template for static frontend hosting plus `/api` proxying.
- Added a systemd service template for the FastAPI backend.
- Corrected the example environment file to match current app defaults.
- Added deployment guidance for the `woody` service account, deploy/admin ownership, and required filesystem permissions, including nginx traverse access for the frontend path.
- Added production guidance for same-origin frontend API configuration and the rebuild or restart steps needed after env changes.
- Added guidance for exposing the site through Cloudflare Tunnel and for disabling the default nginx site when enabling the app site.

## Acceptance criteria coverage
- AC1: Inspect `DEPLOY.md` and `README.md` to confirm the guide covers install, sync, build, migrate, and service startup steps.
- AC2: Inspect `deploy/nginx/woody.conf` to confirm `/` serves frontend assets and `/api/` proxies to `127.0.0.1:8000`.
- AC3: Inspect `deploy/systemd/woody-backend.service` and `.env.example` to confirm the backend service template and example environment match the current application defaults.
- AC4: Inspect `DEPLOY.md` to confirm it documents the `woody` service-account permissions, the deploy/admin split, and the file access needed for systemd and nginx, including nginx traverse access to the parent directories for `frontend/dist`.
- AC5: Inspect `DEPLOY.md` to confirm it recommends `VITE_API_BASE_URL=/api` for production, documents the exact public `FRONTEND_ORIGIN`, and calls out when to rebuild the frontend or restart the backend after env changes.
- AC6: Inspect `DEPLOY.md` to confirm it documents Cloudflare Tunnel routing to local nginx, disabling `/etc/nginx/sites-enabled/default`, and matching nginx `server_name` to the public hostname.

## Validation run
- `make lint`
- `make test`
- `cd frontend && npm test -- --run`

## Risks
- The deployment templates are intentionally generic and still need site-specific values such as domain name, filesystem paths, and production secrets.
