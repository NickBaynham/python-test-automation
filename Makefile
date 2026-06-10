# All recipes invoke tools through pdm run so they work natively on
# macOS, Linux, and Windows (GNU Make via winget or chocolatey).
.PHONY: install lint format test test-unit test-e2e build run security install-browsers docker-build docker-run docker-up docker-down report

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

test-unit:
	pdm run pytest tests/unit

test-e2e:
	pdm run pytest tests/e2e --no-cov

build:
	pdm build

run:
	pdm run python -m testplatform

security:
	pdm run pip-audit

install-browsers:
	pdm run python -m testplatform.browsers

docker-build:
	docker compose build

docker-run:
	docker compose up

docker-up:
	docker compose up -d --wait

docker-down:
	docker compose down

report:
	allure generate allure-results -o allure-report --clean
	allure open allure-report
