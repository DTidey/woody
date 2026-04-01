## Summary
- Port the latest GitHub-enforced workflow guardrails from `aidev` into `woody`.
- Add CodeQL, Dependabot, and CODEOWNERS configuration to keep repository checks explicit in GitHub itself.
- Update local docs, templates, and tests so the exact required checks stay aligned with the new guardrails.

## Spec
- Spec: `docs/specs/12-github-guardrails-sync.md`
- Test plan: `docs/test-plans/12-github-guardrails-sync.md`
- PR draft path: `.ai/pr-description/12-github-guardrails-sync.md`

## Acceptance Criteria
- [x] AC1: `woody` includes `.github/workflows/codeql.yml`, `.github/dependabot.yml`, and `.github/CODEOWNERS`, aligned with the upstream `aidev` GitHub guardrails and repo-specific ownership.
- [x] AC2: Repository docs and PR templates document the GitHub enforcement expectations for `main`, including the exact required checks `CI / test` and `CodeQL / analyze`.
- [x] AC3: `.github/workflows/ci.yml` includes the upstream permission hardening needed for the CI workflow while preserving `woody`'s existing test command behavior.
- [x] AC4: Automated tests verify the new GitHub guardrail files and documented required checks so the ported framework behavior remains enforced locally.

## Security Review
- [x] Security considerations were reviewed and updated in the linked spec
- [x] No meaningful security impact
- [ ] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [x] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - Confirm the required check names in docs and templates match the workflow names GitHub will expose for this repository.

## Validation
- [ ] `make lint`
- [ ] `make test`
- [ ] `make security`

## GitHub Checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`

## Changelog
- [ ] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- Repository rulesets and branch protection still need to be configured in GitHub; the repo changes here only provide the files and documented check names.
