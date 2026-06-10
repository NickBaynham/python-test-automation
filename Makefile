# All recipes invoke tools through pdm run so they work natively on
# macOS, Linux, and Windows (GNU Make via winget or chocolatey).
.PHONY: install lint format test build run security

install:
	pdm install

lint:
	pdm run ruff check src tests
	pdm run ruff format --check src tests
	pdm run mypy src tests

format:
	pdm run ruff format src tests
	pdm run ruff check --fix src tests

test:
	pdm run pytest

build:
	pdm build

run:
	pdm run python -m testplatform

security:
	pdm run pip-audit
