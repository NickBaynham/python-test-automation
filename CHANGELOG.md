# Changelog

## 0.4.0 - 2026-06-10

Phase 3: MongoDB database testing, the full-stack scenario, and the tester guide. Includes the post-phase code review remediation.

### Added

- MongoDB client layer (`testplatform.db`): `MongoTarget` with lazy connections from configuration, collection access, reachability ping, and context-manager lifecycle; new `TP_MONGO_URL` and `TP_MONGO_DATABASE` settings covered by the remote-mode guard (Phase 3, Task 1).
- Test data seeding (`MongoSeeder`): inserts tracked documents and removes exactly what it seeded on cleanup — by id, never dropping collections — with a context-manager form that cleans up even on test failure (Phase 3, Task 2).
- Database state assertions: document existence and absence, field values with per-field mismatch reporting, and query-scoped collection counts (Phase 3, Task 3).
- MongoDB in the compose stack: `mongo:8` on host port 27100, healthcheck with startup backoff, ephemeral by design so every stack start is a clean database (Phase 3, Task 4).
- Database integration suite: seeding, state assertions, and cleanup proven against live MongoDB, with a session-scoped target (fail-fast when down) and a per-test seeder fixture; tests isolate via unique run markers (Phase 3, Task 5).
- Full-stack scenario (`tests/e2e/test_full_stack.py`): a UI action verified through the REST API and down to the MongoDB document, per browser (Phase 3, Task 6).
- Tester guide (`docs/tester-guide.md`): introduction, step-by-step testing at each layer with executed worked examples, test design guidance, and a troubleshooting guide (Phase 3, Task 7).

### Changed

- Sample API now stores items in MongoDB (ObjectId string ids, CORS enabled, depends on the mongo service); sample React app persists items through the API instead of local state, and disables its form while a submission is in flight — fixing an input-loss race the e2e suite caught (Phase 3, Task 6).
- `make security` now also audits the sample API's pinned dependency tree, closing a scanning gap for code shipped in the Docker image (Phase 3 review).

## 0.3.0 - 2026-06-10

Phase 2: REST API testing. Includes the post-phase code review remediation.

### Added

- REST API client layer (`testplatform.api`): `ApiClient` with base URL binding, default headers, bearer auth, timeout, and injectable transport for network-free unit testing; declarative `ApiCall` model with validated HTTP methods (Phase 2, Task 1).
- API response assertions (`testplatform.assertions`): status codes with body context, exact and subset JSON payload checks, and JSON Schema 2020-12 validation reporting all violations (Phase 2, Task 2).
- API target configuration: validated `TP_API_BASE_URL` setting defaulting to the local sample API; remote target mode now requires every target URL explicitly (Phase 2, Task 3).
- Dockerized sample REST API (FastAPI items service, non-root, pinned dependencies) on host port 8100 as the integration reference target, joining the compose stack with a healthcheck (Phase 2, Task 4).
- API integration suite (`tests/integration/`) exercising the client, declarative calls, and every assertion helper against the live sample API, with per-test data cleanup and a fail-fast reachability check; `make test-integration` target and CI step (Phase 2, Task 5).
- `.env.example`: one documented file for local overrides, read by both docker compose and the platform, keeping port and URL pairs together (Phase 2 review).

### Fixed

- JSON assertion helpers fail with the response body in context when it is not JSON, instead of a raw decode traceback (Phase 2 review).
- `assert_matches_schema` validates the schema itself first, so a malformed schema raises a clear `SchemaError` (Phase 2 review).
- CI opts into Node 24 for JavaScript actions ahead of GitHub's June 2026 default switch.

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
