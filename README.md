# python-test-automation

A Python based software test automation platform for testing React UIs, REST APIs, and MongoDB databases, running against dockerized or remote hosted applications.

## Requirements

- Python 3.14 or later
- [PDM](https://pdm-project.org/) (package manager)
- GNU Make
- Docker Desktop (from Phase 1 onward, for dockerized targets)

On Windows, install GNU Make with `winget install GnuWin32.Make` or `choco install make`. All Make recipes are cross-platform: they invoke tools through PDM and use no POSIX-only shell constructs.

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
| `make test` | Run the test suite with coverage (90% minimum) |
| `make build` | Build the sdist and wheel |
| `make run` | Run the platform CLI |
| `make security` | Audit dependencies for known vulnerabilities (pip-audit) |

## Project Layout

```
src/testplatform/    Platform code (typed, src layout)
tests/unit/          Unit tests of the platform's own code
tests/integration/   Application-targeted integration tests (from Phase 1)
tests/e2e/           Application-targeted end-to-end tests (from Phase 1)
```

The distinction matters: `tests/unit/` verifies the platform itself and gates every change; `tests/integration/` and `tests/e2e/` exercise target applications and arrive with later phases.

## Configuration

Settings load from `TP_`-prefixed environment variables (or a local `.env` file), validated by pydantic-settings. Secrets must only ever come from environment variables.

| Variable | Default | Purpose |
|---|---|---|
| `TP_ENVIRONMENT` | `local` | Named environment for the run |
| `TP_TARGET_MODE` | `docker` | Where the application under test runs: `docker` or `remote` |

## Development Workflow

Work is incremental and test-first: write a failing test, implement to green, then `make lint`, `make test`, and `make security` must all pass before a change is done. Coverage below 90% fails the build.

## Documents

- [CHANGELOG.md](CHANGELOG.md) - change log and feature list
- [TODO.md](TODO.md) - features not yet added or under construction

## License

[Apache 2.0](LICENSE)
