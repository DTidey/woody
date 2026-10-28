## Summary
- Regenerate the Python lockfiles with `pip-compile --upgrade` to clear the transitive vulnerabilities that have failed `make security` on every Dependabot PR since 2026-04-08.
- Make the workflow content tests accept any GitHub Action major version so Dependabot action bumps stop breaking `make test`.
- Activate the `protect-main` ruleset so failing checks block auto-merge into `main`.

## Spec
- Spec: `docs/specs/15-dependency-security-refresh.md`
- Test plan: `docs/test-plans/15-dependency-security-refresh.md`
- PR draft path: `.ai/pr-description/15-dependency-security-refresh.md`

## Acceptance criteria
- [x] AC1: `requirements.txt` and `requirements-dev.txt` are regenerated with `pip-compile --upgrade`, and `make security` reports no known vulnerabilities.
- [x] AC2: `tests/test_security_workflow_docs.py` verifies `actions/checkout`, `actions/setup-python`, `actions/github-script`, and `github/codeql-action/{init,autobuild,analyze}` are used at some `@v<major>` version rather than one exact major version, and `make test` passes.
- [x] AC3: `make lint` passes with the upgraded toolchain.
- [x] AC4: The `protect-main` ruleset is `active` for `refs/heads/main` and enforces deletion blocking, non-fast-forward blocking, pull requests with one approval and stale-review dismissal, and required status checks `test`, `analyze (python)`, and `analyze (actions)`.

## Security review
- [x] Security considerations were reviewed and updated in the linked spec
- [ ] No meaningful security impact
- [x] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [x] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - `starlette` moves from `0.52.1` to `1.10.0`; confirm the backend's usage is unaffected beyond the passing smoke tests.

## Validation
- [x] `make lint`
- [x] `make test`
- [x] `make security`

## GitHub checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`

## Changelog
- [x] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- `fastapi.testclient` now emits a `StarletteDeprecationWarning` recommending `httpx2`; tests still pass.
- `AGENTS.md` names `CodeQL / analyze`, but GitHub reports the matrix checks as `analyze (python)` and `analyze (actions)`; the ruleset uses the reported names.
