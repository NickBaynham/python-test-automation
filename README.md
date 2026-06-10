# python-test-automation

A Python based software test automation platform for testing React UIs, REST APIs, and MongoDB databases, running against dockerized or remote hosted applications.

## Requirements

- Python 3.14 or later
- [PDM](https://pdm-project.org/) (package manager)
- GNU Make
- Docker Desktop (for dockerized targets)
- [Allure CLI](https://allurereport.org/docs/install/) for HTML test reports (`brew install allure` on macOS, `scoop install allure` on Windows)

On Windows, install GNU Make with `choco install make` (use a source providing GNU Make 4.x; the GnuWin32 build is outdated). All Make recipes are cross-platform: they invoke tools through PDM and use no POSIX-only shell constructs.

## Setup

```
make install
```

## Make Targets

| Target | Purpose |
|---|---|
| `make install` | Install dependencies via PDM |
| `make lint` | Ruff lint (including security rules), format check, strict mypy |
| `make format` | Apply formatting and safe lint fixes |
| `make test` | Run all tests with coverage (90% minimum); e2e needs the stack up |
| `make test-unit` | Run only the platform unit tests |
| `make test-integration` | Run only the API integration suite (start the stack first: `make docker-up`) |
| `make test-e2e` | Run only the e2e suite (start the stack first: `make docker-up`) |
| `make build` | Build the sdist and wheel |
| `make run` | Run the platform CLI |
| `make security` | Audit dependencies for known vulnerabilities (pip-audit) |
| `make install-browsers` | Detect host browsers, install available Playwright engines, write `config/browsers.json` |
| `make docker-build` | Build the docker compose stack (sample React app, sample REST API, MongoDB) |
| `make docker-up` | Start the stack detached and wait until healthy |
| `make docker-run` | Start the stack in the foreground |
| `make docker-down` | Stop and remove the stack |
| `make report` | Generate and open the Allure HTML report from the last test run |

## Project Layout

```
src/testplatform/    Platform code (typed, src layout)
tests/unit/          Unit tests of the platform's own code
tests/integration/   Application-targeted integration tests (from Phase 1)
tests/e2e/           Application-targeted end-to-end tests (from Phase 1)
```

The distinction matters: `tests/unit/` verifies the platform itself and gates every change; `tests/integration/` (REST API) and `tests/e2e/` (browser) exercise target applications and fail fast with guidance when the stack is not running. E2e tests run headless against every browser marked available in `config/browsers.json` — Playwright engines and system channels (Chrome, Edge) alike — and failures leave a screenshot and Playwright trace under `test-artifacts/`.

## Configuration

Settings load from `TP_`-prefixed environment variables (or a local `.env` file), validated by pydantic-settings. Secrets must only ever come from environment variables.

The dockerized stack provides three reference targets: the sample React app on host port 3100, the sample REST API on host port 8100, and MongoDB on host port 27100 — all shifted off the crowded defaults (3000, 8000, 27017). MongoDB runs without a volume, so every `make docker-up` starts from a clean database. To override, copy [.env.example](.env.example) to `.env`: docker compose and the platform read the same file, which keeps each port and its matching `TP_*_BASE_URL` together.

Browser availability is host-specific generated output: `make install-browsers` writes `config/browsers.json` (git ignored) marking each Playwright engine (chromium, firefox, webkit) and system channel (Chrome, Edge) as available or not. Test fixtures use it to run suites across exactly the browsers the host supports.

| Variable | Default | Purpose |
|---|---|---|
| `TP_ENVIRONMENT` | `local` | Named environment for the run |
| `TP_TARGET_MODE` | `docker` | Where the application under test runs: `docker` or `remote` (values are lowercase) |
| `TP_UI_BASE_URL` | `http://localhost:3100` | Base URL of the UI under test; must be set explicitly when `TP_TARGET_MODE` is `remote` |
| `TP_API_BASE_URL` | `http://localhost:8100` | Base URL of the REST API under test; must be set explicitly when `TP_TARGET_MODE` is `remote` |
| `TP_MONGO_URL` | `mongodb://localhost:27100` | MongoDB instance under test; must be set explicitly when `TP_TARGET_MODE` is `remote` |
| `TP_MONGO_DATABASE` | `sampledb` | Database name holding the application's data |

## Page Objects

E2e tests are written against page objects extending `testplatform.pages.BasePage`. Each page declares its `path` and a readiness locator; `open()` navigates and waits until the page is usable, with no sleeps. Locators follow React-friendly conventions: role-based locators first (`get_by_role`), `data-testid` locators (`get_by_test_id`) where a role would be ambiguous, and no structural CSS or XPath selectors.

To add a page object, subclass `BasePage` under `tests/e2e/pages/`, implement `path` and `ready_locator`, and expose locators and actions as attributes and methods. See [tests/e2e/pages/sample_app.py](tests/e2e/pages/sample_app.py) for the reference example.

## Testing a Remote Application

Point the suites at remote hosted targets by setting the target mode and explicit base URLs — remote mode requires every target URL explicitly:

```
TP_TARGET_MODE=remote TP_UI_BASE_URL=https://app.example.com TP_API_BASE_URL=https://api.example.com make test-e2e test-integration
```

## Continuous Integration

GitHub Actions runs lint, type checks, unit tests with coverage, and the security audit on Linux and Windows; the Docker build and e2e suite run on Linux. Allure results are published as build artifacts, and failing e2e tests upload their screenshots and traces.

## Development Workflow

Work is incremental and test-first: write a failing test, implement to green, then `make lint`, `make test`, and `make security` must all pass before a change is done. Coverage (line and branch) below 90% fails the build.

When running a subset of tests during development, disable the coverage gate, which is calibrated for the full suite: `pdm run pytest tests/unit/test_config.py --no-cov`.

## Documents

- [Tester Guide](docs/tester-guide.md) - how to automate tests with this platform: layer-by-layer how-tos, test design, troubleshooting
- [CHANGELOG.md](CHANGELOG.md) - change log and feature list
- [TODO.md](TODO.md) - features not yet added or under construction

## License

[Apache 2.0](LICENSE)
