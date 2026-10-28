# Dependency Security Refresh

**Spec file:** `docs/specs/15-dependency-security-refresh.md`
**Spec slug:** dependency-security-refresh
**Status:** Done
**Owner:** Claude
**Date:** 2026-10-28

## Problem statement
- Every Dependabot PR since 2026-04-08 failed the `CI / test` job at the `make security` step, yet 92 of them were auto-merged into `main`.
- `pip-audit` reports roughly 48 known vulnerabilities in transitive pins (for example `starlette`, `urllib3`, `anyio`, `certifi`, `idna`, `mako`, `filelock`, `msgpack`, `virtualenv`) that Dependabot does not bump, and `make compile` preserves existing pins, so CI never refreshes them.
- Because `make security` failed first, `make test` was skipped in CI; locally two tests in `tests/test_security_workflow_docs.py` fail because they pin exact GitHub Action major versions that Dependabot has since bumped.
- The `protect-main` repository ruleset exists but is `disabled`, so failing required checks never blocked the Dependabot auto-merge.

## Scope
In scope:
- Regenerate `requirements.txt` and `requirements-dev.txt` with `pip-compile --upgrade` so transitive pins move to non-vulnerable versions.
- Make the GitHub Action version assertions in `tests/test_security_workflow_docs.py` accept any major version while still checking the action is used.
- Activate the `protect-main` ruleset with the protections described in `AGENTS.md` under `## GitHub Enforcement`.

Out of scope / non-goals:
- Changing backend or frontend application behavior.
- Changing the Makefile `compile` target, Dependabot configuration, or the auto-merge workflow.
- Removing the `--ignore-vuln CVE-2026-4539` exclusion (it no longer matches anything but is harmless; leave for a separate change).
- Creating a release.

## Assumptions
- The next available packet prefix is `15`; `14` is reserved by the pending `14-repo-consistency-alignment` packet.
- Upgrading `starlette` from `0.52.1` to `1.10.0` (pulled in by `fastapi==0.162.0`) is acceptable if `make test` passes.
- GitHub Actions approvals count toward the ruleset's required review, because repository workflow permissions allow Actions to approve PRs.

## Ambiguities surfaced
- `AGENTS.md` names the required check `CodeQL / analyze`, but the CodeQL workflow uses a language matrix, so GitHub reports the checks as `analyze (python)` and `analyze (actions)`. The ruleset requires both matrix checks plus `test`. The docs are left unchanged.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `requirements.txt`
  - `requirements-dev.txt`
  - `tests/test_security_workflow_docs.py`
  - `CHANGELOG.md`
- Repository settings affected:
  - Ruleset `protect-main` (id `14596587`)

### Inputs / outputs
- Inputs: `requirements.in`, `requirements-dev.in`, workflow YAML files.
- Outputs:
  - Lockfiles with no known `pip-audit` findings.
  - Workflow content tests that survive Dependabot action-version bumps.
  - An active ruleset that blocks merges into `main` until the required checks pass.
- Error handling: if a required check fails, auto-merge waits instead of merging.

### Examples
```text
$ make security
No known vulnerabilities found
```

## Acceptance criteria
- AC1: `requirements.txt` and `requirements-dev.txt` are regenerated with `pip-compile --upgrade`, and `make security` reports no known vulnerabilities.
- AC2: `tests/test_security_workflow_docs.py` verifies `actions/checkout`, `actions/setup-python`, `actions/github-script`, and `github/codeql-action/{init,autobuild,analyze}` are used at some `@v<major>` version rather than one exact major version, and `make test` passes.
- AC3: `make lint` passes with the upgraded toolchain.
- AC4: The `protect-main` ruleset is `active` for `refs/heads/main` and enforces deletion blocking, non-fast-forward blocking, pull requests with one approval and stale-review dismissal, and required status checks `test`, `analyze (python)`, and `analyze (actions)`.

## Security considerations
- Auth/authz impact: Positive; activating the ruleset prevents merges into `main` without passing checks and an approval.
- Input handling or injection risk: None.
- Secrets or credential handling: None.
- Data exposure or privacy impact: None.
- File system access impact: None.
- Network or external service impact: None beyond existing CI.
- Dependency or supply-chain impact: Positive; removes known-vulnerable transitive pins. `starlette` crosses a major version (`0.52.1` -> `1.10.0`), so reviewers should confirm the API surface the backend uses is unaffected.
- Security notes for reviewers/testers: Confirm `make security` passes without editing the ignore list, and confirm via `gh api repos/DTidey/woody/rulesets/14596587` that enforcement is `active`.

## Edge cases
- Lockfiles are compiled with Python 3.12 locally while CI uses Python 3.11; this matches existing practice and CI resolves with `make compile`.
- A future Dependabot action bump to a new major version must not break the workflow content tests.
- The test helper must not match a different action that shares a prefix (for example `actions/checkout-foo`).

## Test guidance
- AC1 -> `make security`
- AC2 -> `tests/test_security_workflow_docs.py::test_makefile_and_ci_wire_security_automation`, `tests/test_security_workflow_docs.py::test_github_guardrails_files_exist_and_match_documented_checks`, `make test`
- AC3 -> `make lint`
- AC4 -> `gh api repos/DTidey/woody/rulesets/14596587` shows `"enforcement":"active"` and the listed rules

## Decision log
- 2026-10-28: Upgraded all lockfile pins rather than only vulnerable ones, because pip-compile otherwise keeps every stale pin and the test suite passes on the full upgrade.
- 2026-10-28: Required the CodeQL matrix check names as GitHub reports them, instead of the `CodeQL / analyze` label in the docs.
