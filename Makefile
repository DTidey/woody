.PHONY: venv compile sync lint test precommit backend-dev frontend-dev db-up db-down migrate

PYTHON ?= python3

venv:
	$(PYTHON) -m venv .venv

compile:
	. .venv/bin/python -m pip install -U pip setuptools wheel pip-tools
	.venv/bin/pip-compile requirements.in -o requirements.txt
	.venv/bin/pip-compile requirements-dev.in -o requirements-dev.txt

sync:
	.venv/bin/python -m pip install -U pip setuptools wheel pip-tools
	.venv/bin/pip-sync requirements.txt requirements-dev.txt

lint:
	. .venv/bin/activate && ruff check .
	. .venv/bin/activate && ruff format --check .

test:
	. .venv/bin/activate && PYTHONPATH=backend pytest

precommit:
	. .venv/bin/activate && pre-commit run --all-files

backend-dev:
	. .venv/bin/activate && PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

frontend-dev:
	cd frontend && npm install && npm run dev

db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	. .venv/bin/activate && cd backend && alembic upgrade head
