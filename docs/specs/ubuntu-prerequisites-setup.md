# Ubuntu Prerequisites Setup

**Spec slug:** ubuntu-prerequisites-setup
**Status:** In Progress
**Owner:** Codex
**Date:** 2026-03-20

## Problem statement
- The repository has overlapping Ubuntu and deployment setup instructions that disagree on how Python 3.12 should be installed and used.
- This matters because a fresh Ubuntu 22.04 machine can follow the current docs and still fail to create the right virtualenv or run `make sync` due to missing `pip-sync`.

## Scope
In scope:
- Align local Ubuntu setup, README setup, and deployment prerequisites around a consistent Python 3.12 workflow.
- Ensure the documented setup reaches a state where the machine has the prerequisites needed to create the project virtualenv and install dependencies.
- Ensure the Ubuntu setup guide includes the overlapping platform prerequisites called out in deployment docs, including Node.js and nginx installation.
- Ensure the Ubuntu setup guide includes GitHub CLI installation so the machine can authenticate with GitHub.
- Fix the repository setup command path so `make sync` works in a fresh virtualenv.
- Clarify that the Ubuntu setup guide's app run commands are for local development and point production installs to `DEPLOY.md`.

Out of scope / non-goals:
- Changing the application's runtime behavior.
- Reworking the full production deployment architecture.
- Replacing `pip-tools` with another dependency management tool.

## Assumptions
- Ubuntu 22.04 remains a supported local setup target.
- Python 3.12 should be used for this repository's virtual environment on Ubuntu 22.04.
- It is safer to avoid changing Ubuntu's system `python3` interpreter and instead document a safe way to make `python` resolve to Python 3.12 for interactive use.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `Makefile`
  - `README.md`
  - `DEPLOY.md`
  - `docs/setup-ubuntu-22.04.md`
  - `docs/specs/ubuntu-prerequisites-setup.md`
  - `docs/test-plans/ubuntu-prerequisites-setup.md`
  - `.ai/pr-description/ubuntu-prerequisites-setup.md`

### Inputs / outputs
- Inputs:
  - A fresh Ubuntu 22.04 machine
  - Python 3.12 packages installed from apt
  - Repository checkout
- Outputs:
  - Consistent instructions for installing Python 3.12 and creating the repo virtualenv
  - Ubuntu setup instructions that install Node.js and nginx alongside the other prerequisites
  - Ubuntu setup instructions that install GitHub CLI and show how to authenticate it
  - A working `make sync` flow on a fresh virtualenv
  - Deployment instructions that do not rely on an unspecified system default `python`
  - Ubuntu setup instructions that distinguish local development startup from the production deployment path
- Error handling:
  - The Ubuntu guide should explain how to verify which interpreter the virtualenv uses.
  - The Ubuntu guide should explain that changing `/usr/bin/python3` is not recommended.

### Examples
```bash
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip python-is-python3
mkdir -p ~/.local/bin
ln -sf /usr/bin/python3.12 ~/.local/bin/python
python --version
make venv PYTHON=python3.12
make sync
```

## Acceptance criteria
- AC1: `docs/setup-ubuntu-22.04.md`, `README.md`, and `DEPLOY.md` describe a consistent Python 3.12 setup flow that gets a machine to the repository prerequisite stage.
- AC6: `docs/setup-ubuntu-22.04.md` labels `make backend-dev` and `make frontend-dev` as local development commands and points production installs to `DEPLOY.md`.
- AC2: `docs/setup-ubuntu-22.04.md` explains how to make `python` resolve to Python 3.12 safely for interactive use without changing Ubuntu's system `python3`.
- AC3: A fresh project virtualenv can run `make sync` without a prior manual install of `pip-tools`.
- AC4: `docs/setup-ubuntu-22.04.md` includes installation steps for both Node.js and nginx so it reaches the overlapping prerequisite state described by deployment setup.
- AC5: `docs/setup-ubuntu-22.04.md` includes installation and authentication steps for GitHub CLI.

## Edge cases
- A machine may have Python 3.10 as the Ubuntu default while the repo still requires a Python 3.12 virtualenv.
- `python` may be absent unless `python-is-python3` or an explicit shell alias/symlink is configured.
- A user may confuse changing `python` with changing the OS-managed `python3`; the guide should keep those separate.

## Test guidance
- AC1 -> inspect `docs/setup-ubuntu-22.04.md`, `README.md`, and `DEPLOY.md`
- AC2 -> inspect `docs/setup-ubuntu-22.04.md`
- AC3 -> run `make venv PYTHON=python3.12`, then `make sync`
- AC4 -> inspect `docs/setup-ubuntu-22.04.md`
- AC5 -> inspect `docs/setup-ubuntu-22.04.md`
- AC6 -> inspect `docs/setup-ubuntu-22.04.md`

## Decision log
- 2026-03-20: Kept the repository on `pip-tools` and fixed the bootstrap path because it is the smallest change that makes fresh setup work.
- 2026-03-20: Documented a safe `python` default flow via user-level shell path/symlink guidance instead of changing `/usr/bin/python3`.
- 2026-03-20: Kept the Ubuntu guide focused on local machine setup and added an explicit production handoff to `DEPLOY.md` to avoid mixing dev-server commands into deployment guidance.
