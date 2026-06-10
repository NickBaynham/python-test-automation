# Changelog

## 0.1.0 - 2026-06-10

Phase 0: basic Python project.

### Added

- PDM-managed project on Python 3.14 with src layout (`src/testplatform`, typed with a `py.typed` marker).
- Cross-platform Makefile: `install`, `lint`, `format`, `test`, `build`, `run`, `security`.
- Quality tooling: ruff (lint and format, security ruleset enabled), strict mypy, pytest with coverage gated at 90%.
- Dependency vulnerability auditing via pip-audit (`make security`).
- Environment configuration module (`testplatform.config`) built on pydantic-settings: `TP_`-prefixed variables, immutable settings, dockerized or remote hosted target selection.
- CLI entry point (`make run`) reporting the platform version.
- Unit test suite: entry point and configuration module, 100% coverage.

### Feature List

- Environment-driven configuration with validation (local/docker and remote targets).
- Platform CLI stub.

Testing capabilities (React UI, REST API, MongoDB) arrive in later phases; see TODO.md.
