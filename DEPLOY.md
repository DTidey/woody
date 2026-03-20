# Deploying `woody`

This document describes a simple single-server production deployment for `woody`.

## Overview

Recommended production layout:

- PostgreSQL for application data
- FastAPI backend running on `127.0.0.1:8000`
- nginx serving `frontend/dist` and proxying `/api/` to FastAPI
- systemd managing the backend process

Request flow:

- `/` -> static frontend files
- `/api/*` -> backend API

## Server prerequisites

Install or provision:

- Python 3.12+
- Node.js 20+
- PostgreSQL
- nginx
- systemd

Clone the repository onto the server:

```bash
git clone <your-repo-url> /srv/woody
cd /srv/woody
```

On Ubuntu 22.04, install Python 3.12 explicitly instead of relying on the OS default:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
python3.12 --version
```

## Environment

Create a production `.env` at the repo root:

```bash
cp .env.example .env
```

Then set at least:

```dotenv
APP_NAME=Woody API
API_PREFIX=/api
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/jesse_db
FRONTEND_ORIGIN=https://your-domain.example
VITE_API_BASE_URL=/api
```

For production behind nginx, prefer a same-origin API base URL such as `/api` instead of a full browser-facing host name. That keeps frontend requests on the same origin as the site and avoids accidental mismatches with old LAN, localhost, or staging values baked into the frontend build.

Set `FRONTEND_ORIGIN` to the exact public origin that serves the frontend, including the scheme and host, with no trailing slash. Example:

```dotenv
FRONTEND_ORIGIN=https://prod.tidey.co.uk
```

If you change `VITE_API_BASE_URL`, rebuild the frontend so the new value is baked into `frontend/dist`:

```bash
cd frontend
npm ci
npm run build
cd ..
```

If you change `FRONTEND_ORIGIN`, restart the backend service so FastAPI reloads the CORS setting:

```bash
sudo systemctl restart woody-backend
```

## Backend setup

Create and sync the virtualenv:

```bash
make venv PYTHON=python3.12
make sync
```

This avoids depending on whichever interpreter `/usr/bin/python3` currently points to on the server. `make sync` installs `pip-tools` into the virtualenv before running `pip-sync`.

Run database migrations:

```bash
make migrate
```

## Frontend build

Install frontend dependencies and create the production build:

```bash
cd frontend
npm ci
npm run build
cd ..
```

This writes static files to:

```text
frontend/dist/
```

## systemd backend service

Use the template at:

```text
deploy/systemd/woody-backend.service
```

Copy it to the server and adjust:

- `User`
- `Group`
- `WorkingDirectory`
- `EnvironmentFile`
- `ExecStart`

Example install:

```bash
sudo cp deploy/systemd/woody-backend.service /etc/systemd/system/woody-backend.service
sudo systemctl daemon-reload
sudo systemctl enable woody-backend
sudo systemctl start woody-backend
sudo systemctl status woody-backend
```

## Users and permissions

Recommended split:

- `woody`: low-privilege service account that runs the backend process
- deploy/admin user: interactive user that pulls code, installs packages, runs builds and migrations, and manages system services

The `woody` user does not need `sudo`, Docker group access, or permission to bind privileged ports because the backend listens on `127.0.0.1:8000`.

Minimum access for `woody`:

- read and execute access to the app tree under `/srv/woody`
- read access to `/srv/woody/.env`
- execute access to `/srv/woody/.venv/bin/uvicorn`
- network access to PostgreSQL using the credentials in `DATABASE_URL`

nginx also needs read access to `/srv/woody/frontend/dist` so it can serve the built frontend assets. On Ubuntu this usually means the `www-data` user must be able to traverse `/srv`, `/srv/woody`, and `/srv/woody/frontend`, plus read the files under `frontend/dist`.

One practical setup is:

```bash
sudo adduser --system --group --home /srv/woody woody
sudo adduser deployer
sudo usermod -aG sudo deployer
sudo chown -R deployer:woody /srv/woody
sudo find /srv/woody -type d -exec chmod 750 {} \;
sudo find /srv/woody -type f -exec chmod 640 {} \;
sudo chmod 640 /srv/woody/.env
sudo chmod 755 /srv /srv/woody /srv/woody/frontend
sudo find /srv/woody/frontend/dist -type d -exec chmod 755 {} \;
sudo find /srv/woody/frontend/dist -type f -exec chmod 644 {} \;
```

If you prefer to keep `/srv/woody` and `/srv/woody/frontend` more restrictive than `755`, add the nginx user to a group that can traverse those directories and adjust the group permissions accordingly. The important requirement is that nginx can traverse each parent directory in the path to `frontend/dist/index.html`.

With that split:

- the deploy/admin user can update code, run `make sync`, run `make migrate`, and build `frontend/dist`
- the `woody` group grants the backend service read access to the app files
- nginx can traverse the frontend path and read the built frontend assets

If `woody` is only used by systemd, consider disabling interactive shell access:

```bash
sudo usermod -s /usr/sbin/nologin woody
```

## nginx configuration

Use the template at:

```text
deploy/nginx/woody.conf
```

Adjust:

- `server_name`
- frontend `root`
- TLS settings if you terminate HTTPS directly in nginx

Install and reload:

```bash
sudo cp deploy/nginx/woody.conf /etc/nginx/sites-available/woody
sudo ln -sf /etc/nginx/sites-available/woody /etc/nginx/sites-enabled/woody
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

If you still see the default "Welcome to nginx!" page after enabling `woody`, check:

- `server_name` in `/etc/nginx/sites-available/woody` matches the real public hostname
- `/etc/nginx/sites-enabled/default` has been removed or disabled
- `curl -H 'Host: your-domain.example' http://127.0.0.1/` returns your app instead of the nginx welcome page

## Cloudflare Tunnel

If you want to expose the app externally without opening inbound ports to your network, run the site behind a Cloudflare Tunnel and keep nginx as the local web origin.

Recommended shape:

- browser -> `https://your-domain.example`
- Cloudflare Tunnel -> `http://localhost:80`
- nginx -> static frontend and `/api/` proxy
- FastAPI -> `127.0.0.1:8000`

For this setup:

- keep `VITE_API_BASE_URL=/api`
- set `FRONTEND_ORIGIN` to the exact public hostname served through Cloudflare, such as `https://your-domain.example`
- point the tunnel at `http://localhost:80`

If the tunnel is your only public entrypoint, consider binding nginx to localhost only:

```nginx
server {
    listen 127.0.0.1:80;
    server_name your-domain.example;

    root /srv/woody/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

After changing the nginx listener, test and reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Typical Cloudflare Tunnel steps:

1. Create a tunnel in Cloudflare and assign your public hostname.
2. Route that hostname to `http://localhost:80` on the server.
3. Install `cloudflared` on the server and run it as a service.
4. Verify the site loads through the tunnel and `/api/health` works from the public hostname.

If the site loads the default nginx page through the tunnel, nginx is usually serving its default site instead of your `woody` config. Remove `/etc/nginx/sites-enabled/default`, make sure `server_name` matches the tunnel hostname, then reload nginx.

## Rollout checklist

For each deploy:

1. Pull the latest code.
2. Run `make sync`.
3. Run `make migrate`.
4. Build the frontend with `cd frontend && npm ci && npm run build`.
5. Restart the backend service with `sudo systemctl restart woody-backend`.
6. Reload nginx if its config changed.

## Validation

On the server, verify:

```bash
make lint
make test
cd frontend && npm test -- --run
```

Then verify runtime behavior:

```bash
curl http://127.0.0.1:8000/api/health
curl https://your-domain.example/api/health
```

Open the site in a browser and confirm:

- the frontend loads
- `/api/candles/series` returns data
- chart candles load successfully

## Notes

- The frontend is built as static assets and does not need a separate Node server in production.
- Keep the backend bound to `127.0.0.1` and expose it through nginx rather than directly to the internet.
- If you later want TLS automation and simpler config, Caddy would also be a reasonable replacement for nginx.
