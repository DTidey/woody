## Summary
- Upgrade `woody` to the newer workflow version with explicit security review guardrails.
- Require matching PR draft validation alongside spec and test-plan validation.
- Add `make security` and run it in CI for Python static analysis and dependency auditing.

## Spec
- Spec: `docs/specs/11-security-workflow-upgrade.md`
- Test plan: `docs/test-plans/11-security-workflow-upgrade.md`
- PR draft path: `.ai/pr-description/11-security-workflow-upgrade.md`

## Acceptance Criteria
- [x] AC1: Workflow templates, role guidance, and repository docs require explicit security review for code-changing work, including spec security considerations and PR security disposition.
- [x] AC2: PR validation requires a matching PR draft for code-changing work, and the draft must link the same spec and check every acceptance criterion from that spec without unknown AC IDs.
- [x] AC3: The repository exposes `make security`, backed by at least one static security analyzer and one dependency vulnerability audit, and CI runs that command.
- [x] AC4: Tests verify the upgraded validator behavior and the presence of the security workflow wiring so the framework changes remain enforced.

## Security Review
- [x] Security considerations were reviewed and updated in the linked spec
- [x] No meaningful security impact
- [ ] Auth/authz behavior changed
- [ ] Secrets or credential handling changed
- [x] Input validation, data exposure, file access, network access, or dependencies changed
- Reviewer focus:
  - Confirm the temporary audit ignore stays narrow and revisit it once an upstream fix is available.

## Validation
- [x] `make lint`
- [x] `make test`
- [x] `make security`

## Changelog
- [ ] Add to `CHANGELOG.md` under `## Unreleased` if this change should be called out before the next explicit release.

## Open Risks
- `pip-audit` results can change over time as vulnerability data changes.
