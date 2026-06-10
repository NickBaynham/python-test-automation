# Changelog

## Unreleased

### Fixed

- Unit tests are now isolated from a developer's local .env file (tests run from a temporary directory).
- Empty TP_ENVIRONMENT values are rejected at load time instead of being silently accepted.

### Changed

- Version is single-sourced from package metadata; pyproject.toml is the only declaration.
- Coverage now measures branches as well as lines (gate unchanged at 90%).
- README: corrected Windows GNU Make guidance, documented lowercase TP_TARGET_MODE values and the --no-cov flag for subset test runs.

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
