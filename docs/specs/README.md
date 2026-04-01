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
1. Create or update the spec (Spec Writer)
2. Break the spec into tasks and a small commit plan (Orchestrator)
3. Implement strictly to the spec (Implementer)
4. Add tests and the matching test plan (Tester)
5. Review against the spec and acceptance criteria (Reviewer)
6. Merge only when CI is green and behavior matches the spec (Orchestrator)
