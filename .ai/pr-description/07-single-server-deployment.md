- Linked spec: `docs/specs/07-single-server-deployment.md`
- Added a production deployment guide for a single Linux server.
- Added nginx and systemd templates for serving the frontend statically and running the FastAPI backend behind `/api`.
- Corrected the example environment file and deployment docs to match current app defaults, including the existing `jesse_db` database name.
- Added guidance for the `woody` service account, recommended deploy/admin split, and minimum runtime file permissions, including nginx traverse access for the frontend path.
- Clarified that production frontend builds should use `VITE_API_BASE_URL=/api` and that env changes may require a frontend rebuild or backend restart.
- Added deployment guidance for Cloudflare Tunnel and called out the nginx default-site conflict that can produce the welcome page instead of the app.

- [x] AC1: The repository includes a deployment guide describing how to build the frontend, install backend dependencies, run Alembic migrations, and start the backend for production.
- [x] AC2: The repository includes a reverse proxy config template that serves the frontend statically and proxies `/api` requests to the backend service.
- [x] AC3: The repository includes a backend service template and an environment example consistent with the current application defaults, including the existing `jesse_db` database name.
- [x] AC4: `DEPLOY.md` documents the recommended `woody` service-account permissions, the separate deploy/admin responsibilities, and the minimum file access needed for systemd and nginx.
- [x] AC5: `DEPLOY.md` documents production frontend API configuration using a same-origin `VITE_API_BASE_URL=/api`, the exact public `FRONTEND_ORIGIN`, and the rebuild or restart steps required when those values change.
- [x] AC6: `DEPLOY.md` documents how to run the site behind a Cloudflare Tunnel, including routing the tunnel to local nginx, disabling the default nginx site, and matching `server_name` to the public hostname.

- Validation run:
  - `make lint`
  - `make test`
  - `cd frontend && npm test -- --run`

- Open risks:
  - The deployment templates still need site-specific domain names, paths, and secrets before use in a real environment.
