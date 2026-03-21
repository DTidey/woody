# Specs

Each feature/change should have a spec in this folder.

Code-changing specs should also have a matching test plan in `docs/test-plans/<nn>-<slug>.md`.

Naming convention:
- Spec packets use a stable two-digit prefix: `docs/specs/<nn>-<slug>.md`
- Matching test plans use the same filename: `docs/test-plans/<nn>-<slug>.md`
- Matching PR drafts use `.ai/pr-description/<nn>-<slug>.md`
- Use the next available prefix for new work and do not renumber existing packets
- These packet numbers are not release versions; releases belong in `CHANGELOG.md`

Every spec should include:
- Scope and non-goals
- Acceptance criteria labeled `AC1`, `AC2`, ...
- Edge cases and error handling
- Test guidance mapping AC -> tests

Workflow:
1) Create spec (Spec Writer)
2) Implement to spec (Implementer)
3) Add tests (Tester)
4) Review against spec (Reviewer)
5) Merge only when CI is green (Orchestrator)
