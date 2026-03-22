# Technical Environment Document

**Spec file:** `docs/specs/10-technical-environment-document.md`
**Spec slug:** technical-environment-document
**Status:** Draft
**Owner:** Codex
**Date:** 2026-03-22

## Problem statement
- The repository does not yet include a single document that summarizes the application's technical environment in one place.
- This matters because the user wants a reusable reference they can carry into similar projects without re-discovering the stack, runtime assumptions, services, and operating model from scattered files.

## Scope
In scope:
- Add a repository document that describes the current technical environment for `woody`.
- Cover the application architecture, runtime stack, dependencies, environment variables, local workflow, testing toolchain, and deployment shape.
- Make the document reusable as a starting template for similar full-stack projects by including a section structure and prompts that can be adapted.

Out of scope / non-goals:
- Changing runtime behavior, dependency versions, or deployment configuration.
- Introducing automation that generates environment documentation.
- Rewriting existing setup or deployment guides.

## Assumptions
- A documentation-only change is sufficient for the user's request.
- The most useful version of this document should be grounded in the actual repository rather than written as a generic blank template.
- Similar projects will likely share a backend API, frontend SPA, relational database, environment-variable configuration, and a lightweight deployment model.

## Proposed behavior / API
### Public interface
- Files/modules affected:
  - `docs/technical-environment.md`
  - `docs/specs/10-technical-environment-document.md`

### Inputs / outputs
- Inputs:
  - Existing repository documentation and configuration files
  - Current backend, frontend, database, and deployment setup
- Outputs:
  - A technical environment document that explains how the application is structured and run
  - A reusable section layout that can be copied into related projects
- Error handling:
  - If repository details are missing, the document should clearly mark the gaps instead of inventing unsupported details.

### Examples
```text
Technical Environment
- Architecture summary
- Runtime versions and frameworks
- Environment variables
- Local development workflow
- Testing and linting
- Deployment topology
- Reuse notes for similar projects
```

## Acceptance criteria
- AC1: The repository contains a new documentation file that summarizes the current `woody` technical environment, including backend, frontend, database, and deployment layers.
- AC2: The document lists the main runtimes, frameworks, tooling, environment variables, and developer commands used to run and validate the application locally.
- AC3: The document includes a reusable structure or guidance that makes it practical to adapt for similar projects without first reverse-engineering this repository.

## Edge cases
- Some versions are pinned in dependency files while others are described only in setup documentation; the document should distinguish between those sources where helpful.
- Local development and production deployment do not use the same serving model, so both should be described separately.
- The repository includes both general setup docs and project-specific deployment docs; the new document should summarize rather than duplicate them.

## Test guidance
- AC1 -> inspect `docs/technical-environment.md`
- AC2 -> inspect `docs/technical-environment.md` against `README.md`, `Makefile`, `.env.example`, `requirements*.txt`, `frontend/package.json`, and `docker-compose.yml`
- AC3 -> inspect `docs/technical-environment.md` for reusable section guidance

## Decision log
- 2026-03-22: Chose a concrete repository-backed document with reusable headings over a generic empty template so the user gets something immediately useful for both this project and future ones.
