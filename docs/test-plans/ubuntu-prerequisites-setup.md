# Ubuntu Prerequisites Setup

## Summary
- Align the Ubuntu, README, and deployment setup instructions around Python 3.12.
- Document a safe way to make `python` resolve to Python 3.12 for interactive use on Ubuntu 22.04.
- Ensure `make sync` works in a fresh virtualenv by installing `pip-tools` during sync.
- Ensure the Ubuntu setup guide installs both Node.js and nginx as machine prerequisites.
- Ensure the Ubuntu setup guide installs GitHub CLI and includes a GitHub authentication step.
- Ensure the Ubuntu setup guide clearly separates local development startup from the production deployment path.

## Acceptance criteria coverage
- AC1: Inspect `docs/setup-ubuntu-22.04.md`, `README.md`, and `DEPLOY.md` to confirm they use the same Python 3.12 virtualenv setup flow.
- AC2: Inspect `docs/setup-ubuntu-22.04.md` to confirm it recommends a safe user-level `python` default and explicitly avoids changing Ubuntu's system `python3`.
- AC3: Create a fresh virtualenv with `make venv PYTHON=python3.12`, then run `make sync` and confirm dependency sync completes without manually installing `pip-tools`.
- AC4: Inspect `docs/setup-ubuntu-22.04.md` to confirm it includes installation steps for both Node.js and nginx.
- AC5: Inspect `docs/setup-ubuntu-22.04.md` to confirm it includes installation and authentication steps for GitHub CLI.
- AC6: Inspect `docs/setup-ubuntu-22.04.md` to confirm it labels `make backend-dev` and `make frontend-dev` as local development commands and links production installs to `DEPLOY.md`.

## Validation run
- `make venv PYTHON=python3.12`
- `make sync`
- `make lint`
- `make test`

## Risks
- The docs can recommend a safe default `python` path for user shells, but individual shell startup files and PATH ordering may still vary by machine.
