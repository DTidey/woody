# GitHub Guardrails Sync

**Spec file:** `docs/specs/12-github-guardrails-sync.md`
**Spec slug:** github-guardrails-sync
**Status:** Done
**Owner:** Codex
**Date:** 2026-04-01

## Problem statement
- `woody` already documents parts of the newer `aidev` workflow, but it does not yet include all of the GitHub-enforced guardrails that now live in the upstream framework.
- The repository currently lacks repository-managed CodeQL, Dependabot, and CODEOWNERS files, and some local docs/templates do not yet call out the exact required GitHub checks.
- Without these files and the matching documentation/tests, `woody` can drift from the framework and lose the stricter merge protections now expected upstream.

## Scope
In scope:
- Add the missing GitHub guardrail files ported from upstream with repo-appropriate values.
- Update workflow docs and PR templates so they name the exact required checks for merges to `main`.
- Extend tests so the presence and expected contents of the new guardrails stay pinned.

Out of scope / non-goals:
- Changing application runtime behavior in the backend or frontend.
- Creating a release or modifying `CHANGELOG.md`.
- Reworking the existing PR validator beyond what is needed to document and verify the new GitHub-side checks.

## Assumptions
- `woody` should stay aligned with the current `aidev` framework unless a repository-specific difference is necessary.
- The next available packet prefix is `12`.
- The repository owner for `CODEOWNERS` should remain `@DTidey`, matching the current GitHub remote.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `docs/specs/12-github-guardrails-sync.md`
  - `docs/test-plans/12-github-guardrails-sync.md`
  - `.ai/pr-description/12-github-guardrails-sync.md`
  - `AGENTS.md`
  - `README.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.ai/templates/pr_draft_template.md`
  - `.ai/templates/pr_description_template.md`
  - `.github/workflows/ci.yml`
  - `.github/workflows/codeql.yml`
  - `.github/dependabot.yml`
  - `.github/CODEOWNERS`
  - `tests/test_security_workflow_docs.py`

### Inputs / outputs
- Inputs:
  - Upstream `aidev` GitHub workflow guardrail files and wording
  - Local repository workflow docs, templates, and tests
- Outputs:
  - `woody` includes repository-managed GitHub guardrail files for CodeQL, Dependabot, and CODEOWNERS
  - Docs and templates name `CI / test` and `CodeQL / analyze` as the required checks for `main`
  - Tests fail if those guardrail files or documented checks drift
- Error handling:
  - Missing guardrail files should be surfaced by tests rather than silently accepted
  - Repo-specific values should only differ from upstream when needed to keep `woody` accurate

### Examples
```yaml
permissions:
  contents: read
```

```md
## GitHub checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`
```

## Acceptance criteria
- AC1: `woody` includes `.github/workflows/codeql.yml`, `.github/dependabot.yml`, and `.github/CODEOWNERS`, aligned with the upstream `aidev` GitHub guardrails and repo-specific ownership.
- AC2: Repository docs and PR templates document the GitHub enforcement expectations for `main`, including the exact required checks `CI / test` and `CodeQL / analyze`.
- AC3: `.github/workflows/ci.yml` includes the upstream permission hardening needed for the CI workflow while preserving `woody`'s existing test command behavior.
- AC4: Automated tests verify the new GitHub guardrail files and documented required checks so the ported framework behavior remains enforced locally.

## Security considerations
- Auth/authz impact: No application auth changes; this tightens repository governance and review ownership.
- Input handling or injection risk: Low; the added workflows and docs are static configuration.
- Secrets or credential handling: No new secrets are introduced by these changes.
- Data exposure or privacy impact: Low; CodeQL and Dependabot analyze repository contents and dependency metadata in GitHub.
- File system access impact: CI workflows read repository contents as part of analysis.
- Network or external service impact: Dependabot and CodeQL rely on GitHub-managed services.
- Dependency or supply-chain impact: Weekly dependency update automation increases visibility into dependency changes.
- Security notes for reviewers/testers: Confirm the exact required status-check names in docs/templates match the actual workflow names created by the repository.

## Edge cases
- `woody`'s main CI test job still needs `PYTHONPATH=backend pytest`, so the CI workflow should keep that repo-specific behavior even while syncing upstream hardening.
- `CODEOWNERS` must use the actual repository owner rather than blindly copying a placeholder.
- The new tests should assert structure and wording without depending on live GitHub settings.

## Test guidance
- AC1 -> Content tests verify `codeql.yml`, `dependabot.yml`, and `CODEOWNERS` exist and contain the expected upstream guardrails
- AC2 -> Content tests verify `AGENTS.md`, `README.md`, and PR templates mention `CI / test` and `CodeQL / analyze`
- AC3 -> Content tests verify `.github/workflows/ci.yml` includes the permissions block and still runs `make security`
- AC4 -> Run `make lint`, `make test`, and `make security`

## Decision log
- 2026-04-01: Kept `woody`'s repo-specific CI test invocation while otherwise porting the GitHub guardrail files and wording directly from `aidev`.
