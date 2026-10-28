# Changelog

This file records intentionally published project milestones.

Release policy:
- Development packet numbers like `09-release-changelog-policy` are not release numbers.
- Release versions use `MAJOR.MINOR.PATCH` formatting such as `0.1.0`.
- A new release section is created only when explicitly requested.
- Changes can accumulate under `Unreleased` until a release is intentionally cut.

## Unreleased

### Added
- Added a changelog and documented the explicit-release workflow.

### Security
- Refreshed Python lockfiles to clear known vulnerabilities in transitive dependencies and enabled the `main` branch ruleset so failing checks block merges.
