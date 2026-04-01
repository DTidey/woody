## Summary
- Port the newer portable governance automation from `aidev` into `woody`.
- Add the narrow Dependabot validator bypass plus owner and Dependabot maintenance workflows.
- Update workflow tests and action versions while preserving `woody`'s Makefile-driven CI validation flow.

## Spec
- Spec: `docs/specs/13-aidev-governance-sync.md`
- Test plan: `docs/test-plans/13-aidev-governance-sync.md`
- PR draft path: `.ai/pr-description/13-aidev-governance-sync.md`

## Acceptance criteria
- [x] AC1: `.github/scripts/validate_pr.py` in `woody` skips spec validation only for `dependabot[bot]` PRs whose changed files are limited to root dependency manifests and `.github/workflows/*.yml` or `.yaml`, and `tests/test_validate_pr.py` covers both the allow and reject cases.
- [x] AC2: `woody` includes `.github/workflows/auto-approve-own-prs.yml` and `.github/workflows/auto-manage-dependabot-prs.yml` with the same narrow safety constraints now used in `aidev`, and `tests/test_security_workflow_docs.py` verifies those constraints.
- [x] AC3: `woody` updates `.github/workflows/ci.yml` to `actions/checkout@v6` and `actions/setup-python@v6`, creates `.venv` before validation, runs `make compile`, `make sync`, `make lint`, `make security`, and `make test`, updates `.github/workflows/codeql.yml` to `github/codeql-action` `v4`, and preserves `woody`'s Makefile-driven validation flow.
- [x] AC4: The `woody` workflow docs and role docs that describe packet alignment and blocker formatting are updated where needed so the documented process matches the current validation and automation behavior.

## Security review
- [x] Security considerations were reviewed and updated in the linked spec
- [ ] No meaningful security impact
- [x] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [x] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - Confirm the new automation stays tightly scoped to safe maintenance cases and does not widen approval or merge authority beyond the intended PR classes.

## Validation
- [x] `make lint`
- [x] `make test`
- [x] `make security`

## GitHub checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`

## Changelog
- [ ] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- The auto-approval and auto-merge flows still depend on GitHub repository settings allowing Actions approval and pull-request auto-merge.
