# fastapi-tests-design

Plan, review and implement deterministic tests for FastAPI backends, especially JWT authentication and PostgreSQL behavior.

The repository is named `fastapi-test-design`; the public skill remains **`fastapi-tests-design`**. Install its files in a directory with that plural name. No repository rename is required.

The skill distinguishes unit, API/integration, auth and database behavior. It covers lifespan ownership, guaranteed override cleanup, transaction isolation around commits and extra connections, and fail-closed test environment checks. It adapts to existing architecture and does not impose SQLAlchemy, JWT or a new application factory.

## Installation

### AI Marketplace

The plugin is distributed through `inprojects-ai-tools` from this repository's `plugin/` directory, pinned to tag `v1.1.0`. After the tag and marketplace update are published, install it in Claude Code:

```text
/plugin install fastapi-tests-design@inprojects-ai-tools
```

For Codex, refresh the marketplace and select `fastapi-tests-design` in the plugin directory, or use the commands supported by your installed CLI. The contained skill is `fastapi-tests-design`. For UI design, the existing plugin selector `ui-design` is preserved.

### Standalone project or user installation

Keep a source checkout outside the application's skills directory, then export only the skill files. This avoids a nested `.git` directory and excludes generated plugin copies and evaluations:

```sh
skill_checkout=$(mktemp -d)
git clone --branch v1.1.0 --depth 1 https://github.com/inprojectspl/fastapi-test-design.git "$skill_checkout/source"
mkdir -p .claude/skills/fastapi-tests-design
git -C "$skill_checkout/source" archive HEAD SKILL.md references | tar -x -C .claude/skills/fastapi-tests-design
```

Commit that ordinary directory in the parent project. For Claude user installation replace the destination with `~/.claude/skills/fastapi-tests-design`. For Codex use `.agents/skills/fastapi-tests-design` or `~/.agents/skills/fastapi-tests-design`. Copy both `SKILL.md` and `references/`; copying only the entrypoint is insufficient. Existing root-level `SKILL.md` paths remain available.

To update, review the next release, fetch/check out its tag in the source checkout, repeat the archive export and commit the resulting diff. Review removed reference files as well; archive extraction does not delete obsolete files.

If the team deliberately uses submodules, configure one explicitly instead of committing an ordinary nested clone:

```sh
git submodule add https://github.com/inprojectspl/fastapi-test-design.git .claude/skills/fastapi-tests-design
git -C .claude/skills/fastapi-tests-design checkout v1.1.0
git add .gitmodules .claude/skills/fastapi-tests-design
```

Other clones need `git submodule update --init --recursive` (or `git clone --recurse-submodules`). To update, fetch/check out the new tag within the submodule and commit the new gitlink in the parent. A submodule includes authoring/package files; prefer the archive method when only skill resources should be installed.

## Usage and results

- "Plan tests for this auth module" returns boundaries, scenarios, assumptions and fixture/isolation choices without editing code.
- "Review these repository tests" returns findings with locations and consequences.
- "Add a regression for cross-user access" writes tests within scope, runs the narrowest relevant command and reports results or blockers.

References cover async client/lifespan setup, database isolation and the conditional auth matrix. Tests of PostgreSQL semantics require PostgreSQL; ordinary unit tests do not need a database. No production DSN fallback or cleanup of unverified shared resources is allowed.

## Maintenance and verification

`SKILL.md` and `references/` at the repository root are the authoring sources. `plugin/.claude-plugin/plugin.json` holds the release metadata. The generated `plugin/skills/`, portable `plugin/plugin.json` and compatibility `.codex-plugin/plugin.json` are committed so installing a tag requires no build step:

```sh
python3 scripts/package_plugin.py
python3 scripts/package_plugin.py --check
claude plugin validate plugin
```

This preserves standalone source paths while providing conventional plugin packaging for both runtimes. Generated files must not be edited directly. No MCP server, hook, extra permission or explicit-only invocation policy is required.

See [evaluation record](evals/README.md) for audit decisions, executable examples, exact versions and limitations. Example execution and agent behavioral evaluation are separate. See [CHANGELOG](CHANGELOG.md) for releases.
