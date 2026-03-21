# Release Changelog Policy

**Spec file:** `docs/specs/09-release-changelog-policy.md`
**Spec slug:** release-changelog-policy
**Status:** Draft
**Owner:** Codex
**Date:** 2026-03-21

## Problem statement
- The repository does not yet define how shipped milestones should be recorded separately from the numbered spec/test-plan packets.
- This matters because development packet numbers explain implementation order, while releases should describe intentionally published milestones in a stable, user-facing form.

## Scope
In scope:
- Add a top-level `CHANGELOG.md`.
- Define release version formatting as `MAJOR.MINOR.PATCH`.
- Define that new releases are created only when explicitly requested.
- Define an `Unreleased` section for work that has landed but is not yet part of a release.
- Update the repo workflow docs and PR template to reference the changelog policy.

Out of scope / non-goals:
- Automating release creation or git tagging.
- Backfilling historical released versions.
- Enforcing changelog updates in CI.

## Assumptions
- The project can remain in `0.x.y` versions until the release cadence and compatibility expectations are clearer.
- Not every merged spec packet should become a release immediately.
- The user will explicitly ask when a new release should be cut.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `CHANGELOG.md`
  - `AGENTS.md`
  - `README.md`
  - `docs/specs/README.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.ai/templates/pr_description_template.md`

### Inputs / outputs
- Inputs:
  - Merged project changes
  - An explicit user request to create a release
- Outputs:
  - A changelog with an `Unreleased` section
  - Versioned release sections in `n.n.n` format created only on request
  - Workflow guidance that distinguishes spec packet numbers from release numbers
- Error handling:
  - If no release has been requested, changes remain in `Unreleased`.
  - If a change is too minor for immediate versioning, it can still be documented without cutting a release.

### Examples
```text
CHANGELOG.md
- Unreleased
  - Added release-policy documentation.

When explicitly requested:
- 0.1.0 - 2026-03-21
  - First intentionally cut project release.
```

## Acceptance criteria
- AC1: The repository includes a top-level `CHANGELOG.md` with an `Unreleased` section and guidance that release sections use `MAJOR.MINOR.PATCH` formatting.
- AC2: `AGENTS.md` and `README.md` state that releases are created only on explicit request and clarify that numbered spec packets are not release numbers.
- AC3: Workflow-facing templates or docs used during PR preparation reference the changelog policy so contributors know where release notes belong before a release is cut.

## Edge cases
- Several spec packets may accumulate in `Unreleased` before the next release is requested.
- Documentation-only changes may still appear in `Unreleased` without forcing a new version.
- A release may be requested even if the project is still using `0.x.y` versions.

## Test guidance
- AC1 -> inspect `CHANGELOG.md`
- AC2 -> inspect `AGENTS.md` and `README.md`
- AC3 -> inspect `.github/PULL_REQUEST_TEMPLATE.md` and `.ai/templates/pr_description_template.md`

## Decision log
- 2026-03-21: Chose explicit release requests over automatic version bumps so releases reflect intentional milestones rather than every merged packet.
