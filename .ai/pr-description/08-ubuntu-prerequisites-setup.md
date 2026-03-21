- Linked spec: `docs/specs/08-ubuntu-prerequisites-setup.md`
- Aligned the Ubuntu setup guide, README, and deployment guide around an explicit Python 3.12 virtualenv workflow.
- Added guidance for making `python` resolve to Python 3.12 safely on Ubuntu 22.04 without changing the system `python3`.
- Fixed the bootstrap path so `make sync` installs `pip-tools` before calling `pip-sync` in a fresh virtualenv.
- Added nginx to the Ubuntu prerequisite guide so it matches the overlapping platform setup described by deployment docs.
- Added GitHub CLI installation and authentication steps to the Ubuntu prerequisite guide.
- Clarified that `make backend-dev` and `make frontend-dev` are local development commands and pointed production installs to `DEPLOY.md`.

- [x] AC1: `docs/setup-ubuntu-22.04.md`, `README.md`, and `DEPLOY.md` describe a consistent Python 3.12 setup flow that gets a machine to the repository prerequisite stage.
- [x] AC2: `docs/setup-ubuntu-22.04.md` explains how to make `python` resolve to Python 3.12 safely for interactive use without changing Ubuntu's system `python3`.
- [x] AC3: A fresh project virtualenv can run `make sync` without a prior manual install of `pip-tools`.
- [x] AC4: `docs/setup-ubuntu-22.04.md` includes installation steps for both Node.js and nginx so it reaches the overlapping prerequisite state described by deployment setup.
- [x] AC5: `docs/setup-ubuntu-22.04.md` includes installation and authentication steps for GitHub CLI.
- [x] AC6: `docs/setup-ubuntu-22.04.md` labels `make backend-dev` and `make frontend-dev` as local development commands and points production installs to `DEPLOY.md`.

- Validation run:
  - `make venv PYTHON=python3.12`
  - `make sync`
  - `make lint`
  - `make test`

- Open risks:
  - User shell PATH ordering can still differ across machines, so the optional user-level `python` symlink guidance may need minor adaptation per shell profile.
