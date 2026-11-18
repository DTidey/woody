## Summary
- Let the auto-approve workflow approve repository-owner PRs from `hermes/` branches (Hermes agent PRs) as well as `codex/`.
- The owner check stays mandatory; only the branch-prefix check gains an OR.
- Trigger, permissions, and steps are unchanged.

## Spec
- Spec: `docs/specs/17-auto-approve-hermes-branches.md`
- Test plan: `docs/test-plans/17-auto-approve-hermes-branches.md`
- PR draft path: `.ai/pr-description/17-auto-approve-hermes-branches.md`

## Acceptance criteria
- [x] AC1: The `auto-approve` job condition requires `github.event.pull_request.user.login == github.repository_owner` AND a head ref starting with `codex/` or `hermes/` (the OR is parenthesised so the owner check always applies).
- [x] AC2: The workflow trigger (`pull_request_target` on `main`), permissions (`pull-requests: write`), and approve step are unchanged, and the workflow YAML parses.
- [x] AC3: `tests/test_security_workflow_docs.py` asserts the full parenthesised condition, and `make lint`, `make test`, and `make security` pass.

## Security review
- [x] Security considerations were reviewed and updated in the linked spec
- [ ] No meaningful security impact
- [x] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [ ] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - Confirm the parentheses around the `||` so a non-owner `hermes/` PR cannot be auto-approved.

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
- Auto-approval scope widens to a second owner-only branch prefix; any automation the owner runs on `hermes/` branches will get an approval without human review.
