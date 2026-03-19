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
  software-properties-common
```

## 2. Install Python 3.12

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

## 3. Install Node.js

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

## 4. Install Docker Engine with Compose

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

## 5. Create the project environment file

From the repo root:

```bash
cp .env.example .env
```

Then update `DATABASE_URL` in `.env` so it matches the local Docker database created by `docker-compose.yml`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/woody
```

This matters because the checked-in `.env.example` currently points to `jesse_db`, while the local PostgreSQL container creates a database named `woody`.

## 6. Create the Python virtual environment

From the repo root:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip setuptools wheel
make sync
```

Use `python3.12 -m venv .venv` instead of `make venv` on Ubuntu 22.04 unless your default `python` already points to Python 3.12.

Verify the interpreter inside the venv:

```bash
. .venv/bin/activate
python --version
```

## 7. Start PostgreSQL and run migrations

```bash
make db-up
make migrate
```

## 8. Run the app

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

## 9. Validate the environment

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

### `python -m venv .venv` uses Python 3.10

That means Ubuntu is still using the system default interpreter. Recreate the environment with:

```bash
rm -rf .venv
python3.12 -m venv .venv
. .venv/bin/activate
make sync
```

### `docker compose` fails with permission errors

Your shell session probably does not yet have the updated `docker` group membership. Log out and back in, then retry.

### `make migrate` cannot connect to PostgreSQL

Check both of these:

- `make db-up` completed successfully
- `DATABASE_URL` in `.env` points to the `woody` database on port `5432`
