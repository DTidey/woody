# AIDev Governance Sync

**Spec file:** `docs/specs/13-aidev-governance-sync.md`
**Spec slug:** aidev-governance-sync
**Status:** Done
**Owner:** Codex
**Date:** 2026-04-01

## Problem statement
- `woody` already adopted the earlier security workflow and GitHub guardrail updates, but it still lags behind the newer repository-governance automation now present in `aidev`.
- The current `woody` PR validator still blocks safe Dependabot dependency and workflow updates, even though `aidev` now exempts that narrow class of bot-authored maintenance PRs.
- `woody` also lacks the newer maintenance workflows that auto-approve owner-authored `codex/` branches and auto-manage safe Dependabot PRs, and its CI/workflow tests still pin older action versions.

## Scope
In scope:
- Port the narrow Dependabot PR validation exception from `aidev` into `woody`.
- Add the missing GitHub Actions workflows for owner-maintenance auto-approval and safe Dependabot auto-management.
- Update `woody` CI and CodeQL workflow pins to the current portable `aidev` versions while preserving `woody`'s repo-specific install, lint, security, and test commands.
- Update tests and lightweight workflow docs/role docs so the new governance behavior is documented and enforced locally.

Out of scope / non-goals:
- Replacing `woody`'s application-specific `README.md` content with `aidev`'s app-agnostic repository README.
- Porting `aidev`-specific optional template files that are not used by `woody`'s current workflow.
- Changing `woody`'s backend/frontend product behavior.
- Creating a release or changing `CHANGELOG.md`.

## Assumptions
- The next available packet prefix in `woody` is `13`.
- `woody` should preserve its repo-specific CI commands such as direct `pip-compile`, direct `pip install`, `ruff`, and `PYTHONPATH=backend pytest` rather than copying `aidev`'s Makefile-wrapped CI steps verbatim.
- The auto-approval workflow should remain tightly scoped to PRs into `main` where the author matches the repository owner and the branch starts with `codex/`.
- The Dependabot auto-management workflow should stay limited to dependency manifest changes and `.github/workflows/*.yml` or `.yaml` updates.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `docs/specs/13-aidev-governance-sync.md`
  - `docs/test-plans/13-aidev-governance-sync.md`
  - `.ai/pr-description/13-aidev-governance-sync.md`
  - `.github/scripts/validate_pr.py`
  - `.github/workflows/ci.yml`
  - `.github/workflows/codeql.yml`
  - `.github/workflows/auto-approve-own-prs.yml`
  - `.github/workflows/auto-manage-dependabot-prs.yml`
  - `tests/test_validate_pr.py`
  - `tests/test_security_workflow_docs.py`
  - `docs/specs/README.md`
  - `docs/test-plans/README.md`
  - `docs/specs/00-ai-workflow-guardrails.md`
  - `docs/test-plans/00-ai-workflow-guardrails.md`
  - `.ai/roles/01_orchestrator.md`
  - `.ai/roles/02_implementer.md`

### Inputs / outputs
- Inputs:
  - Pull request author metadata, base branch, head branch, and changed file list
  - CI workflow executions on pushes and pull requests
  - Repository docs/tests that pin expected governance behavior
- Outputs:
  - Safe Dependabot dependency/workflow PRs can bypass spec validation
  - Owner-authored `codex/` maintenance PRs can be auto-approved
  - Safe Dependabot PRs can be auto-approved and queued for auto-merge
  - `woody` tests pin the current portable governance behavior and workflow versions
- Error handling:
  - Dependabot PRs that touch disallowed files continue through normal spec validation
  - Auto-management should refuse empty or disallowed changed-file sets
  - If GitHub repository settings do not allow Actions approval or auto-merge, the workflows should fail visibly rather than silently succeeding

### Examples
```text
Dependabot dependency-only PR detected; skipping spec validation.
```

```text
Dependabot PR not eligible for auto-management.
```

## Acceptance criteria
- AC1: `.github/scripts/validate_pr.py` in `woody` skips spec validation only for `dependabot[bot]` PRs whose changed files are limited to root dependency manifests and `.github/workflows/*.yml` or `.yaml`, and `tests/test_validate_pr.py` covers both the allow and reject cases.
- AC2: `woody` includes `.github/workflows/auto-approve-own-prs.yml` and `.github/workflows/auto-manage-dependabot-prs.yml` with the same narrow safety constraints now used in `aidev`, and `tests/test_security_workflow_docs.py` verifies those constraints.
- AC3: `woody` updates `.github/workflows/ci.yml` to `actions/checkout@v6` and `actions/setup-python@v6`, updates `.github/workflows/codeql.yml` to `github/codeql-action` `v4`, and preserves `woody`'s repo-specific CI commands.
- AC4: The `woody` workflow docs and role docs that describe packet alignment and blocker formatting are updated where needed so the documented process matches the current validation and automation behavior.

## Security considerations
- Auth/authz impact: Limited repository-governance impact; the new workflows can approve and queue merges, so they must stay tightly scoped to safe maintenance cases.
- Input handling or injection risk: Low; decisions are based on GitHub event metadata and repository-controlled filenames.
- Secrets or credential handling: Uses the repository GitHub token only; no new secrets are introduced.
- Data exposure or privacy impact: None beyond standard pull-request metadata access in GitHub Actions.
- File system access impact: No new local file-access behavior; CI continues to read repository files for linting, tests, and validation.
- Network or external service impact: Uses GitHub Actions, GitHub REST APIs, the GitHub CLI, and GitHub-hosted CodeQL analysis.
- Dependency or supply-chain impact: Positive overall; this keeps dependency-maintenance flows current and updates security-scanning action versions.
- Security notes for reviewers/testers: Verify the automation cannot approve or auto-merge source-code changes or non-targeted branch/author combinations, and verify the CodeQL/CI action version bumps do not change required check names.

## Edge cases
- Dependabot PRs that mix dependency/workflow updates with backend, frontend, or test-file changes must still require normal spec validation.
- Workflow-only Dependabot PRs under `.github/workflows/` should qualify for the validator bypass and auto-management.
- Empty file lists must not qualify for Dependabot automation.
- `woody`'s CI must keep using its own compile/install/test commands even while action versions are updated.
- Docs-only PRs should remain exempt from spec enforcement.

## Test guidance
- AC1 -> Unit tests verify accepted Dependabot file lists and rejected source-file lists in `tests/test_validate_pr.py`
- AC2 -> Content tests verify the owner-approval and Dependabot auto-management workflows, permissions, branch filters, author checks, file filters, approval command, and auto-merge command
- AC3 -> Content tests verify `actions/checkout@v6`, `actions/setup-python@v6`, and `github/codeql-action/{init,autobuild,analyze}@v4` while preserving `woody`'s repo-specific CI commands
- AC4 -> Run `make lint`, `make test`, and `make security`

## Decision log
- 2026-04-01: Ported only the portable governance/process changes from `aidev` and intentionally kept `woody`'s application-specific README and CI command shape intact.
