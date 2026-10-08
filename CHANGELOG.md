# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-10-08

### Added

- Added focused lifespan, database-isolation and auth-matrix references with executable lifecycle and PostgreSQL examples.
- Added generated marketplace plugin packages preserving the public skill name fastapi-tests-design.

### Changed

- Separated proportional plan, review and implementation contracts with independent expectations and actual verification results.
- Clarified commit/savepoint isolation, multiple-connection limits, conditional JWT claims and cross-user resource checks.
- Updated installation to include references and distinguish repository and skill names.

### Fixed

- Required explicit lifecycle ownership and guaranteed dependency-override restoration.
- Required verified isolated test targets before mutations, migrations or cleanup, without production configuration fallback.

## [1.0.0] - 2026-04-01

### Added
- Initial release of the `fastapi-tests-design` Claude Skill.
- `SKILL.md` with:
  - explicit test-type classification heuristics,
  - FastAPI/JWT/PostgreSQL-specific testing playbook,
  - fixture architecture and determinism guidance,
  - security-focused negative testing requirements,
  - anti-pattern rejection rules,
  - mandatory output contract and quality gate.
- `README.md` with installation, usage, and design principles.
- `CLAUDE.md` contributor and repository policy guidance.

[Unreleased]: https://github.com/inprojectspl/fastapi-test-design/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/inprojectspl/fastapi-test-design/releases/tag/v1.1.0
[1.0.0]: https://github.com/inprojectspl/fastapi-test-design/tree/cc45a7047080650c7c487926abc4cc36867f11a6
