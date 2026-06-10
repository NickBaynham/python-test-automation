# Changelog

## 0.2.0 - 2026-06-10

Phase 1: React UI testing with Playwright. Includes the post-phase code review remediation.

### Fixed

- E2e failure-artifact capture is exception-safe: a crashed page no longer loses the trace or leaks the browser context.
- System browser channels (Chrome, Edge) marked available are now actually driven by the e2e suite, not just recorded.
- A corrupt config/browsers.json now skips the e2e suite with a hint instead of aborting the whole test run.
- Inventory and artifact paths are anchored to the project root, so the suite behaves the same from any working directory.
- Artifact filenames derive from the full test nodeid, preventing collisions between same-named tests in different modules.
- The blank-input e2e test asserts against a settled list state and can no longer false-pass.

### Changed

- The remote-mode configuration guard generalizes over a declared field list, ready for Phase 2/3 target settings.
- Channel detection covers Linux install paths and microsoft-edge-stable.
- CI: ubuntu jobs invoke Make targets directly (single source of truth); the Windows job runs only OS-dependent checks (unit tests, pip-audit); Playwright browsers are cached between runs.
- The sample app dependency tree is locked (package-lock.json, npm ci).
- The compose healthcheck probes fast only during startup, backing off to 30s steady-state.

### Added

- Browser detection and installation (`make install-browsers`): detects Playwright engines and system browser channels (Chrome, Edge) on the host, installs available engines, and writes the git-ignored availability inventory `config/browsers.json` (Phase 1, Task 1).
- Playwright as a runtime dependency.
- Page object foundation (`testplatform.pages.BasePage`): navigation against per-environment base URLs, explicit readiness contract, React-friendly locator conventions (role-based and test-id; structural selectors disallowed) (Phase 1, Task 2).
- UI target configuration: validated `TP_UI_BASE_URL` setting, defaulting to the local sample app; remote target mode refuses to run on a defaulted URL (Phase 1, Task 3).
- Dockerized sample React app (Vite, served by unprivileged nginx) on host port 3100 as the e2e reference target, with compose healthcheck and Make targets `docker-build`, `docker-run`, `docker-up`, `docker-down` (Phase 1, Task 4).
- Allure reporting: every `make test` run emits results to `allure-results/`; `make report` generates and opens the HTML report (Phase 1, Task 5).
- E2e suite for the sample React app: page object (`SampleAppPage`), fixtures parametrizing tests across the browsers in `config/browsers.json`, failure screenshots and traces in `test-artifacts/`, and Make targets `test-unit` / `test-e2e` (Phase 1, Task 6).
- GitHub Actions pipeline: lint, format, type check, unit tests with coverage, and security audit on Linux and Windows; Docker build and e2e suite on Linux with Allure results and failure artifacts uploaded (Phase 1, Task 7).

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
