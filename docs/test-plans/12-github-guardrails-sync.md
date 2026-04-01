# Test Plan: github-guardrails-sync

Path: `docs/test-plans/12-github-guardrails-sync.md`

## What changed
- Added the missing GitHub-managed guardrail files for CodeQL, Dependabot, and CODEOWNERS.
- Updated repository docs and PR templates to name the required checks for merges to `main`.
- Hardened the CI workflow permissions while keeping `woody`'s existing test invocation.

## Acceptance criteria coverage
- AC1: Verify `.github/workflows/codeql.yml`, `.github/dependabot.yml`, and `.github/CODEOWNERS` exist with the expected upstream-style contents.
- AC2: Verify `AGENTS.md`, `README.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.ai/templates/pr_draft_template.md`, and `.ai/templates/pr_description_template.md` mention `CI / test` and `CodeQL / analyze`.
- AC3: Verify `.github/workflows/ci.yml` includes the `permissions` block, still runs `make security`, and preserves `PYTHONPATH=backend pytest`.
- AC4: Run `make lint`, `make test`, and `make security`.

## Edge cases
- From spec:
  - `woody` keeps its repo-specific CI test command while syncing upstream guardrails.
  - CODEOWNERS must match the actual repository owner.
  - Tests should pin structure without depending on live GitHub settings.
- Additional adversarial cases:
  - Docs mention branch protection generally but omit the exact required status-check names.
  - CodeQL workflow exists but scans the wrong languages or omits the analysis action.
  - Dependabot is present for Python but not GitHub Actions updates.

## Notes
- Flaky risks: None expected from the structural tests; only `pip-audit` data can vary over time during `make security`.
- Determinism considerations: Prefer content assertions for GitHub config files, then rely on the existing command suite for end-to-end validation.
