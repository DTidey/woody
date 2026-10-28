# Test Plan: repo-consistency-alignment

Path: `docs/test-plans/14-repo-consistency-alignment.md`

## What changed
- Tightened docs-only detection so human-authored dependency and tooling changes require the normal spec-first packet.
- Backfilled packet `00` so it now has the companion PR draft and security-review context expected by the current workflow.
- Added tests that pin both the validator classification and the lightweight workspace-setting sync from `aidev`.

## Acceptance criteria coverage
- AC1: Verify validator tests reject docs-only classification for dependency manifests, `Makefile`, and pre-commit config, while still allowing `README.md` and `CHANGELOG.md`.
- AC2: Verify packet `00` has a matching PR draft and a `Security considerations` section in the spec.
- AC3: Run `make lint`, `make test`, and `make security`, and verify static tests cover the historical packet and workspace setting.
- AC4: Verify `.vscode/settings.json` contains `"makefile.configureOnOpen": false`.

## Edge cases
- From spec:
  - `CHANGELOG.md` should stay docs-only.
  - Dependabot dependency-only PRs should still qualify for the existing bypass.
  - Packet `00` backfill should not affect runtime behavior.
  - The VS Code setting should not affect CLI or CI execution.
- Additional adversarial cases:
  - A future validator edit re-classifies `pyproject.toml` as docs-only again.
  - Packet `00` loses its PR draft because it is treated as "historical."
  - The workspace setting drifts and VS Code starts auto-configuring Makefile integration on open again.

## Notes
- Flaky risks: None expected; coverage is static content plus pure validator unit tests.
- Determinism considerations: Prefer direct file-content assertions over narrative review.
