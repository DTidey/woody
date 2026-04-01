# Repo Consistency Alignment

**Spec file:** `docs/specs/14-repo-consistency-alignment.md`
**Spec slug:** repo-consistency-alignment
**Status:** Done
**Owner:** Codex
**Date:** 2026-04-01

## Problem statement
- `woody` still treats several dependency and tooling files as docs-only in PR validation even though its written workflow says code-changing PRs must carry a matching packet.
- Historical packet `00` predates the current workflow requirements, so it still lacks the matching PR draft and security-review context that the repository now expects.
- The latest `aidev` base-repo changes also added a small VS Code workspace default that avoids noisy Makefile auto-configuration prompts.

## Scope
In scope:
- Tighten docs-only detection so human-authored dependency and tooling changes require the normal spec-first packet flow.
- Keep true documentation-only changes such as `README.md` and `CHANGELOG.md` exempt from spec validation.
- Backfill packet `00` so it includes the companion PR draft and security considerations expected by the current repository rules.
- Add tests that pin the stricter validator behavior, the packet `00` backfill, and the workspace setting.
- Add the `.vscode/settings.json` workspace default from `aidev`.

Out of scope / non-goals:
- Retrofitting every older `woody` product packet that predates explicit security-considerations sections.
- Changing application behavior in the backend or frontend.
- Redesigning the overall spec-first workflow.
- Creating a release or editing `CHANGELOG.md` beyond keeping it docs-only for validator purposes.

## Assumptions
- Root documentation files such as `README.md` and `CHANGELOG.md` should remain docs-only.
- Dependency manifests, `Makefile`, and `.pre-commit-config.yaml` are workflow-affecting code changes for human-authored PRs.
- Historical packet `00` can be updated for workflow consistency without changing shipped behavior.
- Disabling VS Code Makefile auto-configuration on open is safe for this repository because the Makefile is intentionally run through explicit commands.

## Proposed behavior / API
### Public interface
- Functions/classes/modules affected:
  - `.github/scripts/validate_pr.py`
  - `tests/test_validate_pr.py`
  - `tests/test_security_workflow_docs.py`
  - `docs/specs/00-ai-workflow-guardrails.md`
  - `.ai/pr-description/00-ai-workflow-guardrails.md`
  - `.vscode/settings.json`
- CLI entry points (if any):
  - None

### Inputs / outputs
- Inputs:
  - Changed file paths during PR validation
  - Historical packet `00` workflow artifacts
  - VS Code workspace settings loaded on repository open
- Outputs:
  - Human-authored dependency and tooling PRs require the normal spec packet flow
  - `README.md` and `CHANGELOG.md` remain docs-only for validator purposes
  - Packet `00` now matches the current repository workflow expectations
  - VS Code no longer prompts to auto-configure Makefile integration when the workspace opens
- Error handling:
  - Validator failures should continue to explain missing packet artifacts clearly
  - Historical packet alignment is enforced by static tests so future drift is caught quickly

### Examples
```text
Changed files:
- pyproject.toml

Result:
- PR requires linked spec, matching test plan, and matching PR draft
```

```text
Changed files:
- README.md
- CHANGELOG.md

Result:
- PR is treated as docs-only
```

## Acceptance criteria
- AC1: `.github/scripts/validate_pr.py` treats dependency and tooling files such as `pyproject.toml`, `requirements*.in`, `requirements*.txt`, `Makefile`, and `.pre-commit-config.yaml` as code-changing inputs for human-authored PRs, while keeping `README.md` and `CHANGELOG.md` docs-only.
- AC2: Packet `00` includes a matching PR draft and its spec includes the security-review information required by the current repository rules.
- AC3: Tests verify the stricter docs-only classification, the packet `00` artifact alignment, and the VS Code workspace setting so the ported behavior remains enforced.
- AC4: `woody` includes `.vscode/settings.json` with `"makefile.configureOnOpen": false` to match the latest `aidev` workspace default.

## Security considerations
- Auth/authz impact: None; this packet affects repository workflow validation and editor defaults only.
- Input handling or injection risk: Low; validator logic remains path-based and repository-controlled.
- Secrets or credential handling: None.
- Data exposure or privacy impact: None.
- File system access impact: Read-only access to repository files in tests and validation; the VS Code setting only changes editor behavior.
- Network or external service impact: None beyond existing CI usage.
- Dependency or supply-chain impact: Tighter validation reduces the chance of unreviewed dependency and tooling changes bypassing the documented workflow.
- Security notes for reviewers/testers: Confirm docs-only detection stays narrow and that packet `00` backfill improves consistency without changing runtime behavior.

## Edge cases
- `CHANGELOG.md` must remain docs-only even though it lives at the repository root.
- Dependabot dependency-only PRs should still use the existing narrow bypass path from packet `13`.
- Packet `00` backfill should not change validator behavior for active product code.
- The VS Code setting should not affect command-line workflows or CI behavior.

## Test guidance
- AC1 -> Validator unit tests verify dependency and tooling files are not treated as docs-only while `README.md` and `CHANGELOG.md` still are
- AC2 -> Static tests verify packet `00` includes both a security considerations section and a matching PR draft
- AC3 -> `tests/test_security_workflow_docs.py`, `tests/test_validate_pr.py`, `make lint`, `make test`, and `make security`
- AC4 -> Static tests verify `.vscode/settings.json` contains `"makefile.configureOnOpen": false`

## Decision log
- 2026-04-01: Ported the latest `aidev` consistency changes into `woody` with a minimal historical backfill limited to packet `00`, leaving broader legacy packet retrofits for a separate decision.
