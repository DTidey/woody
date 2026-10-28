# Test Plan: dependency-security-refresh

Path: `docs/test-plans/15-dependency-security-refresh.md`

## What changed
- Regenerated `requirements.txt` and `requirements-dev.txt` with `pip-compile --upgrade` to clear `pip-audit` findings in transitive pins.
- Relaxed GitHub Action version assertions in `tests/test_security_workflow_docs.py` to accept any major version.
- Activated the `protect-main` ruleset so failing checks block merges into `main`.

## Acceptance criteria coverage
- AC1: Run `make security` and confirm `No known vulnerabilities found`.
- AC2: Run `make test`; `test_makefile_and_ci_wire_security_automation` and `test_github_guardrails_files_exist_and_match_documented_checks` pass against the current `@v7`/`@v9`/`@v4` workflow pins.
- AC3: Run `make lint`.
- AC4: Run `gh api repos/DTidey/woody/rulesets/14596587` and confirm `enforcement` is `active` with `deletion`, `non_fast_forward`, `pull_request`, and `required_status_checks` (`test`, `analyze (python)`, `analyze (actions)`) rules.

## Edge cases
- From spec:
  - A future major action bump must not fail the workflow content tests.
  - The helper must not match an action name that only shares a prefix.
- Additional adversarial cases:
  - Removing an action from a workflow entirely must still fail the tests.

## Notes
- Flaky risks: `pip-audit` results change as new advisories are published.
- Determinism considerations: Lockfile versions are pinned; CI's `make compile` keeps them.
