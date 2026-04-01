# Test Plan: aidev-governance-sync

Path: `docs/test-plans/13-aidev-governance-sync.md`

## What changed
- Ported the newer `aidev` governance automation into `woody`, including the narrow Dependabot validator bypass and the owner/Dependabot maintenance workflows.
- Updated `woody` CI and CodeQL workflow pins to current portable action versions while preserving the Makefile-driven validation flow.
- Updated tests and lightweight workflow docs so the documented process matches the enforced behavior.

## Acceptance criteria coverage
- AC1: Verify `.github/scripts/validate_pr.py` includes the Dependabot allowlist helpers and bypass path, and `tests/test_validate_pr.py` covers both accepted and rejected file sets.
- AC2: Verify `.github/workflows/auto-approve-own-prs.yml` and `.github/workflows/auto-manage-dependabot-prs.yml` exist with the expected branch/author/file constraints, then verify `tests/test_security_workflow_docs.py` pins those workflow details.
- AC3: Verify `.github/workflows/ci.yml` uses `actions/checkout@v6`, `actions/setup-python@v6`, `make venv`, `make compile`, `make sync`, `make lint`, `make security`, and `make test`, and verify `.github/workflows/codeql.yml` uses `github/codeql-action/{init,autobuild,analyze}@v4`.
- AC4: Run `make lint`, `make test`, and `make security`.

## Edge cases
- From spec:
  - Dependabot PRs with source-code changes must not bypass normal validation.
  - Workflow-only Dependabot PRs under `.github/workflows/` should still qualify.
  - Empty file lists must not qualify for Dependabot automation.
  - `woody` must create `.venv` before any Makefile target that activates it.
- Additional adversarial cases:
  - The validator bypass is accidentally widened to any bot-authored PR.
  - The auto-management workflow allows non-workflow, non-dependency file changes.
  - CI updates action versions but accidentally switches away from `woody`'s current lint/test commands.

## Notes
- Flaky risks: Low for content tests; `pip-audit` data can still vary over time during `make security`.
- Determinism considerations: Prefer content assertions and focused unit tests, then rely on the required `make` suite for end-to-end validation.
