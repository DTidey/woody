# Auto-approve Hermes Branches

**Spec file:** `docs/specs/17-auto-approve-hermes-branches.md`
**Spec slug:** auto-approve-hermes-branches
**Status:** Done
**Owner:** Claude
**Date:** 2026-11-18

## Problem statement
- `.github/workflows/auto-approve-own-prs.yml` approves only repository-owner PRs from `codex/` branches (introduced in `docs/specs/13-aidev-governance-sync.md`).
- The owner now also opens agent PRs from `hermes/` branches via the Hermes agent, and those still need a manual approval to satisfy the `main` ruleset.

## Scope
In scope:
- Extend the auto-approve job condition so the branch check accepts `codex/` or `hermes/`, keeping the repository-owner check mandatory.
- Pin the new condition in `tests/test_security_workflow_docs.py`.
- Record the change in `CHANGELOG.md` under `## Unreleased`.

Out of scope / non-goals:
- Changing the workflow trigger, permissions, or steps.
- Changing the Dependabot auto-manage workflow.
- Editing the historical packet `13-aidev-governance-sync`; this spec supersedes its `codex/`-only wording.
- Creating a release.

## Assumptions
- The next available packet prefix is `17` (`16` is taken by `16-opentelemetry-api-cve-fix`).
- `hermes/` branches are only created by the repository owner's Hermes agent; the owner check is what actually restricts approval.

## Ambiguities surfaced
- None.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `.github/workflows/auto-approve-own-prs.yml`
  - `tests/test_security_workflow_docs.py`
  - `CHANGELOG.md`

### Inputs / outputs
- Inputs: `pull_request_target` events for PRs into `main`.
- Outputs: an approving review when the PR author is the repository owner and the head branch starts with `codex/` or `hermes/`; otherwise the job is skipped.
- Error handling: unchanged.

### Examples
```yaml
if: >-
  github.event.pull_request.user.login == github.repository_owner &&
  (startsWith(github.event.pull_request.head.ref, 'codex/') ||
   startsWith(github.event.pull_request.head.ref, 'hermes/'))
```

## Acceptance criteria
- AC1: The `auto-approve` job condition requires `github.event.pull_request.user.login == github.repository_owner` AND a head ref starting with `codex/` or `hermes/` (the OR is parenthesised so the owner check always applies).
- AC2: The workflow trigger (`pull_request_target` on `main`), permissions (`pull-requests: write`), and approve step are unchanged, and the workflow YAML parses.
- AC3: `tests/test_security_workflow_docs.py` asserts the full parenthesised condition, and `make lint`, `make test`, and `make security` pass.

## Security considerations
- Auth/authz impact: Slightly widens auto-approval to a second owner-only branch prefix. A non-owner PR from a `hermes/` branch is still not approved, because the owner check is ANDed with the parenthesised prefix check.
- Input handling or injection risk: None; the condition compares event fields and the step only interpolates `html_url`, as before. No PR code is checked out under `pull_request_target`.
- Secrets or credential handling: None; still uses the scoped `github.token`.
- Data exposure or privacy impact: None.
- File system access impact: None.
- Network or external service impact: None.
- Dependency or supply-chain impact: None.
- Security notes for reviewers/testers: Confirm the parentheses around the `||` so operator precedence cannot bypass the owner check.

## Edge cases
- Owner PR from `hermes/x` -> approved.
- Owner PR from `codex/x` -> approved (unchanged).
- Owner PR from `feature/x` or `hermesfoo/x` -> not approved.
- Non-owner PR from `hermes/x` or `codex/x` -> not approved.

## Test guidance
- AC1 -> `tests/test_security_workflow_docs.py::test_github_guardrails_files_exist_and_match_documented_checks`
- AC2 -> same test (trigger/permission/step assertions) plus `yaml.safe_load` of the workflow
- AC3 -> `make lint`, `make test`, `make security`

## Decision log
- 2026-11-18: Kept a single job with an OR'd prefix check rather than a second job, to keep the workflow minimal.
