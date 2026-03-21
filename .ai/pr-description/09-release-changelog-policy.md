## Summary
- Added a top-level `CHANGELOG.md` with an `Unreleased` section and `MAJOR.MINOR.PATCH` release guidance.
- Documented that releases are created only when explicitly requested.
- Clarified across workflow docs and PR templates that numbered spec packets are not release numbers.

## Spec
- `docs/specs/09-release-changelog-policy.md`
- `docs/test-plans/09-release-changelog-policy.md`

## Acceptance Criteria
- [x] AC1: The repository includes a top-level `CHANGELOG.md` with an `Unreleased` section and guidance that release sections use `MAJOR.MINOR.PATCH` formatting.
- [x] AC2: `AGENTS.md` and `README.md` state that releases are created only on explicit request and clarify that numbered spec packets are not release numbers.
- [x] AC3: Workflow-facing templates or docs used during PR preparation reference the changelog policy so contributors know where release notes belong before a release is cut.

## Validation
- [x] `make lint`
- [x] `make test`

## Open Risks
- Release cutting and tag creation are still manual by design, so consistency depends on continuing to follow the documented workflow.
