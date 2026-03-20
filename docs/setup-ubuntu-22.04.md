# Ubuntu 22.04 Environment Setup

This project uses:

- Python for the FastAPI backend, Alembic migrations, linting, and tests
- Node.js for the Vite frontend
- Docker Compose for the local PostgreSQL database

The safest local setup on Ubuntu 22.04 is to use Python 3.12 for the virtual environment, because the pinned dependency files in this repo were compiled with Python 3.12.

## 1. Install system packages

Update apt metadata and install the base tools:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  curl \
  git \
  ca-certificates \
  gnupg \
  lsb-release \
  make \
  software-properties-common
```

## 2. Install Python 3.12 prerequisites

Ubuntu 22.04 ships with Python 3.10 by default, so install Python 3.12 explicitly:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

Verify it:

```bash
python3.12 --version
```

## 3. Optional: make `python` resolve to Python 3.12 for your shell

Ubuntu 22.04 uses `python3.10` as its system-managed `python3`. Do not replace `/usr/bin/python3` with Python 3.12.

If you want the plain `python` command in your own shell to resolve to Python 3.12, use a user-level symlink instead:

```bash
mkdir -p ~/.local/bin
ln -sf /usr/bin/python3.12 ~/.local/bin/python
export PATH="$HOME/.local/bin:$PATH"
hash -r
python --version
```

If you want that PATH change to persist for future shells, add it to your shell profile such as `~/.profile` or `~/.bashrc`.

## 4. Install Node.js

The frontend needs Node.js. Node 20 LTS is a good default on Ubuntu 22.04:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify it:

```bash
node --version
npm --version
```

## 5. Install nginx

The deployment guide assumes nginx is available on the machine. Install it now so the box already has that prerequisite:

```bash
sudo apt install -y nginx
```

Verify it:

```bash
nginx -v
systemctl status nginx --no-pager
```

## 6. Install GitHub CLI

Install the GitHub CLI so the machine is ready to authenticate with GitHub and work with pull requests from the terminal:

```bash
sudo apt install -y gh
```

Verify it and authenticate:

```bash
gh --version
gh auth login
gh auth status
```

## 7. Install Docker Engine with Compose

This repo uses Docker Compose for PostgreSQL. If Docker is not already installed:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

After adding yourself to the `docker` group, log out and log back in before using Docker without `sudo`.

Verify it:

```bash
docker --version
docker compose version
```

## 8. Create the project environment file

From the repo root:

```bash
cp .env.example .env
```

Then update `DATABASE_URL` in `.env` so it matches the local Docker database created by `docker-compose.yml`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/woody
```

This matters because the checked-in `.env.example` currently points to `jesse_db`, while the local PostgreSQL container creates a database named `woody`.

## 9. Create the Python virtual environment

From the repo root:

```bash
make venv PYTHON=python3.12
. .venv/bin/activate
python --version
make sync
```

This creates the virtualenv with Python 3.12 explicitly. `make sync` now installs `pip-tools` into the virtualenv before running `pip-sync`, so you do not need a separate manual `pip-tools` install.

Verify the interpreter inside the venv:

```bash
. .venv/bin/activate
python --version
.venv/bin/pip-sync --version
```

You should see Python 3.12.x from inside the virtualenv.

## 10. Start PostgreSQL and run migrations

```bash
make db-up
make migrate
```

## 11. Run the app locally

These commands start the local development servers. They are useful for validating the machine setup and developing on the app, but they are not the production runtime path.

If you are installing this on a production server, use [`DEPLOY.md`](../DEPLOY.md) instead. Production in this repo means:

- build the frontend into static assets with `npm run build`
- run the backend as a systemd service
- serve the frontend and proxy `/api` through nginx

Backend:

```bash
make backend-dev
```

Frontend, in another terminal:

```bash
make frontend-dev
```

Endpoints:

- Backend API: `http://localhost:8000/api`
- Frontend dev server: `http://localhost:5173`

## 12. Validate the environment

Backend checks:

```bash
make lint
make test
```

Frontend tests:

```bash
cd frontend
npm test -- --run
```

## Troubleshooting

### `make venv PYTHON=python3.12` fails because `python3.12` is not found

The Python 3.12 packages were not installed successfully. Re-run the Python install step and verify:

```bash
python3.12 --version
apt-cache policy python3.12
```

### `python --version` still shows Python 3.10 in my shell

That is separate from the project virtualenv. The repo will still work as long as you create the venv with `make venv PYTHON=python3.12`.

If you want plain `python` in your shell to resolve to Python 3.12, repeat the user-level symlink step and make sure `~/.local/bin` appears before `/usr/bin` in your PATH:

```bash
printf '%s\n' "$PATH"
which python
python --version
```

### `pip-sync` is not found

Inside this repo, `make sync` installs `pip-tools` into `.venv` before calling `pip-sync`. If a previous setup left the virtualenv in a bad state, recreate it:

```bash
rm -rf .venv
make venv PYTHON=python3.12
make sync
```

You can verify the installed command directly:

```bash
.venv/bin/pip-sync --version
```

### `docker compose` fails with permission errors

Your shell session probably does not yet have the updated `docker` group membership. Log out and back in, then retry.

### `make migrate` cannot connect to PostgreSQL

Check both of these:

- `make db-up` completed successfully
- `DATABASE_URL` in `.env` points to the `woody` database on port `5432`
