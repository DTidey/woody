# Test Plan: auto-approve-hermes-branches

Path: `docs/test-plans/17-auto-approve-hermes-branches.md`
Spec: `docs/specs/17-auto-approve-hermes-branches.md`

## What changed
- `.github/workflows/auto-approve-own-prs.yml` now accepts owner PRs from `codex/` or `hermes/` branches.
- `tests/test_security_workflow_docs.py` pins the new parenthesised condition.

## Acceptance criteria coverage
- AC1: `test_github_guardrails_files_exist_and_match_documented_checks` asserts the owner check followed by `(codex/ || hermes/)` in parentheses.
- AC2: The same test still asserts `pull_request_target:`, `branches: [main]`, `pull-requests: write`, and the `gh pr review ... --approve` step; `python -c "import yaml; yaml.safe_load(open('.github/workflows/auto-approve-own-prs.yml'))"` succeeds.
- AC3: Run `make lint`, `make test`, `make security`.

## Edge cases
- From spec:
  - Non-owner PRs from either prefix are not approved (owner check is ANDed outside the parentheses).
  - Branches that merely start with `hermes` without a slash are not approved.
- Additional adversarial cases:
  - Removing the parentheses would let `hermes/` PRs from any author be approved; the full-condition assertion catches this.

## Notes
- Flaky risks: None.
- Determinism considerations: Content-based test; no network.
