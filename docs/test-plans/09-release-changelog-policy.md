# Test Plan: release-changelog-policy

Path: `docs/test-plans/09-release-changelog-policy.md`

## What changed
- Added a top-level changelog for released and unreleased work.
- Defined `MAJOR.MINOR.PATCH` release formatting.
- Defined that releases are created only on explicit request.
- Updated workflow docs and PR templates to reference the changelog policy.

## Acceptance criteria coverage
- AC1: Inspect `CHANGELOG.md` to confirm it includes an `Unreleased` section and describes `MAJOR.MINOR.PATCH` release sections.
- AC2: Inspect `AGENTS.md` and `README.md` to confirm they distinguish numbered spec packets from release numbers and require explicit release requests.
- AC3: Inspect `.github/PULL_REQUEST_TEMPLATE.md` and `.ai/templates/pr_description_template.md` to confirm they reference the changelog workflow.

## Edge cases
- Multiple merged packets can remain in `Unreleased` before any release is requested.
- The changelog can document changes without creating a release section immediately.
- Early project releases can remain in the `0.x.y` range.

## Notes
- Validation is documentation inspection only; no runtime behavior changes are involved.
