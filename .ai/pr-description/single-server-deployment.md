- Linked spec: `docs/specs/single-server-deployment.md`
- Added a production deployment guide for a single Linux server.
- Added nginx and systemd templates for serving the frontend statically and running the FastAPI backend behind `/api`.
- Corrected the example environment file and deployment docs to match current app defaults, including the existing `jesse_db` database name.

- [x] AC1: The repository includes a deployment guide describing how to build the frontend, install backend dependencies, run Alembic migrations, and start the backend for production.
- [x] AC2: The repository includes a reverse proxy config template that serves the frontend statically and proxies `/api` requests to the backend service.
- [x] AC3: The repository includes a backend service template and an environment example consistent with the current application defaults, including the existing `jesse_db` database name.

- Validation run:
  - `make lint`
  - `make test`
  - `cd frontend && npm test -- --run`

- Open risks:
  - The deployment templates still need site-specific domain names, paths, and secrets before use in a real environment.
