# fastapi-tests-design

A production-oriented Claude Skill for planning and implementing high-quality tests in **FastAPI + JWT + PostgreSQL** backends.

This repository provides a single installable skill (`SKILL.md`) focused on practical test architecture, explicit test-type boundaries, deterministic execution, and security-aware coverage.

## What this skill does

The skill helps Claude:
- classify test targets correctly (unit vs integration vs API vs auth/security vs DB-bound),
- design robust fixture and isolation strategies,
- cover JWT auth and permission failure paths,
- avoid flaky async/database patterns,
- produce concrete, implementation-ready test plans.

## When to use

Use `fastapi-tests-design` when you need to:
- create a test plan for an existing FastAPI backend,
- add tests for JWT authentication or authorization rules,
- redesign test architecture for determinism and maintainability,
- review an existing test suite for blind spots and anti-patterns.

## Repository structure

```text
fastapi-tests-design/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── CLAUDE.md
```

## Installation

### Option A: Project-level installation

Copy `SKILL.md` into your project skills directory:

```bash
mkdir -p .claude/skills/fastapi-tests-design
cp SKILL.md .claude/skills/fastapi-tests-design/SKILL.md
```

### Option B: User-level installation

```bash
mkdir -p ~/.claude/skills/fastapi-tests-design
cp SKILL.md ~/.claude/skills/fastapi-tests-design/SKILL.md
```

### Option C: Install directly from GitHub

```bash
git clone https://github.com/inprojectspl/fastapi-test-design /tmp/fastapi-test-design
mkdir -p ~/.claude/skills/fastapi-tests-design
cp /tmp/fastapi-test-design/SKILL.md ~/.claude/skills/fastapi-tests-design/SKILL.md
```

For project-level installation from the cloned repository:

```bash
mkdir -p .claude/skills/fastapi-tests-design
cp /tmp/fastapi-test-design/SKILL.md .claude/skills/fastapi-tests-design/SKILL.md
```

## Usage examples

Prompt examples that should trigger this skill:
- "Design unit and integration tests for my FastAPI auth module."
- "Review this JWT test suite and find security blind spots."
- "Help me define pytest fixtures for async FastAPI with PostgreSQL."
- "Create a test classification map for services, routers, and repositories."

## Design principles

This skill is intentionally opinionated:
1. **Boundary-first**: don’t mix unit and integration concerns.
2. **Security-aware**: include negative auth and permission cases by default.
3. **Deterministic**: control time/UUID/env/randomness when behavior depends on them.
4. **Isolation-focused**: explicit DB/session/override cleanup to prevent flaky tests.
5. **Operational output**: plans must be directly implementable.

## Limitations

- This skill provides strategy and implementation guidance; it does not assume one specific ORM or migration stack.
- For framework-specific details (e.g., plugin edge cases), repository context is still required.
- If your architecture is not layered (routes/services/repositories), the skill will first normalize boundaries before proposing tests.

## Versioning

This project follows SemVer. See [CHANGELOG.md](./CHANGELOG.md) for release history.
