# Test Plan: security-workflow-upgrade

Path: `docs/test-plans/11-security-workflow-upgrade.md`

## What changed
- Upgraded `woody`'s workflow templates, role guidance, and docs to include explicit security review.
- Tightened PR validation to require matching PR drafts with linked-spec and AC alignment.
- Added automated security checks via `make security` and CI wiring.

## Acceptance criteria coverage
- AC1: Verify templates, role docs, and repository docs contain the expected security review sections and prompts.
- AC2: Verify validator tests cover PR draft path derivation, matching spec links, missing ACs, and unknown ACs.
- AC3: Verify `Makefile`, requirements, and CI define and run `make security`.
- AC4: Run `make lint`, `make test`, and `make security`.

## Edge cases
- From spec:
  - Python-side security automation is added first even though the repository also has a frontend.
  - Temporary audit ignores must be explicit and documented.
  - Docs-only changes should still avoid code-change workflow requirements.
  - Historical packets should not require retroactive artifact invention.
- Additional adversarial cases:
  - PR validation checks a PR draft path but fails to verify the linked spec or AC checklist.
  - `make security` exists in the Makefile but CI bypasses it.
  - Templates mention security generally but give no explicit no-impact path.

## Notes
- Flaky risks: Vulnerability audit results can change over time as advisory data changes.
- Determinism considerations: Keep structural tests focused on file contents and command wiring, then run the live security command during validation.
