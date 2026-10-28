## Summary
- Align `woody`'s validator with the latest `aidev` rule that dependency and tooling changes count as code changes for human-authored PRs.
- Backfill packet `00` so it matches the repository's current companion-artifact and security-review expectations.
- Sync the small VS Code workspace setting that suppresses automatic Makefile configuration on open.

## Spec
- Spec: `docs/specs/14-repo-consistency-alignment.md`
- Test plan: `docs/test-plans/14-repo-consistency-alignment.md`
- PR draft path: `.ai/pr-description/14-repo-consistency-alignment.md`

## Acceptance Criteria
- [x] AC1: `.github/scripts/validate_pr.py` treats dependency and tooling files such as `pyproject.toml`, `requirements*.in`, `requirements*.txt`, `Makefile`, and `.pre-commit-config.yaml` as code-changing inputs for human-authored PRs, while keeping `README.md` and `CHANGELOG.md` docs-only.
- [x] AC2: Packet `00` includes a matching PR draft and its spec includes the security-review information required by the current repository rules.
- [x] AC3: Tests verify the stricter docs-only classification, the packet `00` artifact alignment, and the VS Code workspace setting so the ported behavior remains enforced.
- [x] AC4: `woody` includes `.vscode/settings.json` with `"makefile.configureOnOpen": false` to match the latest `aidev` workspace default.

## Security Review
- [x] Security considerations were reviewed and updated in the linked spec
- [x] No meaningful security impact
- [ ] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [x] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - Confirm the validator stays strict for human-authored dependency and tooling changes while packet `00` and the workspace setting remain low-risk backfills.

## Validation
- [x] `make lint`
- [x] `make test`
- [x] `make security`

## GitHub Checks
- Required checks for `main`:
  - `CI / test`
  - `CodeQL / analyze`

## Changelog
- [ ] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- Broader historical `woody` feature packets still predate explicit spec security-considerations sections and may merit a separate cleanup packet later.
