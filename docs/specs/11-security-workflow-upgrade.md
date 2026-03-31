# Security Workflow Upgrade

**Spec file:** `docs/specs/11-security-workflow-upgrade.md`
**Spec slug:** security-workflow-upgrade
**Status:** Done
**Owner:** Codex
**Date:** 2026-03-31

## Problem statement
- `woody` uses an older version of the spec-first workflow and does not yet include the newer security review and automated security validation guardrails.
- The repository already enforces specs, test plans, and acceptance-criteria checklists, but it does not require explicit security review in specs and PR materials.
- The current PR validator also does not enforce matching PR drafts as tightly as the latest framework version.

## Scope
In scope:
- Upgrade workflow docs, templates, and role guidance to include explicit security review expectations.
- Strengthen PR validation so code-changing PRs require a matching PR draft with the same spec link and AC coverage.
- Add a `make security` command backed by Python security tooling and run it in CI.
- Add tests that keep the upgraded workflow behavior pinned.

Out of scope / non-goals:
- Adding frontend-specific JavaScript security tooling in this phase.
- Reworking unrelated application behavior in the backend or frontend.
- Changing deployment behavior, environment-variable behavior, or release policy.

## Assumptions
- `woody` should stay aligned with the newer framework used in `aidev`, with small repo-specific adaptation for its FastAPI backend.
- The most useful initial automated security checks for this repository are Python-focused because the current workflow tooling and validator are Python-based and the backend is FastAPI.
- A temporary vulnerability ignore may be necessary if the audit reports an advisory with no available fix version.
- Existing workflow packet numbering stays stable, so the next available packet prefix is `11`.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `AGENTS.md`
  - `README.md`
  - `.github/workflows/ci.yml`
  - `.github/scripts/validate_pr.py`
  - `.ai/templates/spec_template.md`
  - `.ai/templates/pr_draft_template.md`
  - `.ai/templates/pr_description_template.md`
  - `.ai/templates/review_checklist.md`
  - `.ai/roles/03_tester.md`
  - `.ai/roles/04_reviewer.md`
  - `Makefile`
  - `requirements-dev.in`
  - `requirements-dev.txt`
  - `tests/test_validate_pr.py`
  - `tests/test_security_workflow_docs.py`

### Inputs / outputs
- Inputs:
  - Code-changing specs, PR bodies, and PR drafts
  - Python source under `backend/app` and workflow automation under `.github/scripts`
  - `requirements.txt` and `requirements-dev.txt`
- Outputs:
  - Specs and PR materials explicitly record security considerations
  - PR validation requires a matching PR draft aligned with the linked spec and acceptance criteria
  - `make security` runs automated checks locally and in CI
- Error handling:
  - If security impact is unclear, the workflow should surface that as a blocker rather than assuming no impact
  - If the dependency audit reports an unfixed advisory, any temporary ignore should be documented explicitly

### Examples
```bash
make security
```

```md
## Security considerations
- Auth/authz impact: None
- Input handling or injection risk: Route query handling changed
- Secrets or credential handling: None
- Security notes for reviewers/testers: Verify parameter validation and response filtering.
```

## Acceptance criteria
- AC1: Workflow templates, role guidance, and repository docs require explicit security review for code-changing work, including spec security considerations and PR security disposition.
- AC2: PR validation requires a matching PR draft for code-changing work, and the draft must link the same spec and check every acceptance criterion from that spec without unknown AC IDs.
- AC3: The repository exposes `make security`, backed by at least one static security analyzer and one dependency vulnerability audit, and CI runs that command.
- AC4: Tests verify the upgraded validator behavior and the presence of the security workflow wiring so the framework changes remain enforced.

## Security considerations
- Auth/authz impact: None directly; this is workflow and validation tooling.
- Input handling or injection risk: Low; the validator and security commands use fixed repository-controlled invocations.
- Secrets or credential handling: Security tooling should not require credentials for normal local or CI use.
- Data exposure or privacy impact: Low; checks operate on repository contents and dependency metadata.
- File system access impact: Read-only scanning of source files and dependency manifests.
- Network or external service impact: `pip-audit` may need live vulnerability metadata during execution.
- Dependency or supply-chain impact: Introduces development-only security tooling that must be pinned in compiled requirements.
- Security notes for reviewers/testers: Verify temporary audit ignores are documented and narrow in scope.

## Edge cases
- `woody` includes backend and frontend code, but this phase only adds Python-side automated security checks.
- The repository may inherit the same `pygments` advisory currently seen in the framework repo; if so, the ignore should be documented rather than hidden.
- PR validation must still allow docs-only changes without requiring spec artifacts.
- Existing PR draft packets start at `03`, so new validation should only require drafts for future code-changing work, not retroactively invent missing drafts for historical packets.

## Test guidance
- AC1 -> Content checks verify security sections exist in the upgraded templates, role docs, and repository documentation
- AC2 -> Validator unit tests verify PR draft path derivation, spec linkage, and AC coverage rules
- AC3 -> Content checks verify `Makefile`, `requirements-dev.in`, and CI include the security command/tooling
- AC4 -> Run `make lint`, `make test`, and `make security`

## Decision log
- 2026-03-31: Combined the newer framework upgrades into one repository packet so `woody` can move from the older workflow version to the current one in a single reviewable change.
