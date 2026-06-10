# To Do

Features not yet added or under construction, in planned order.

## Phase 1: React UI Testing with Playwright

- Playwright for Python with page object pattern (role/test-id locators).
- Sample React application in docker compose as the reference target.
- Docker targets in the Makefile (`docker-build`, `docker-run`, `docker-up`, `docker-down`).
- Allure HTML reporting (`make report`); results published in CI.
- GitHub Actions pipeline: lint, type checks, unit tests, and security audit on a Linux and Windows matrix; Docker-based suites on Linux runners.
- Failure artifacts: screenshots and traces.

## Phase 2: REST API Testing

- httpx-based client layer and declarative API test model.
- Assertion helpers: status codes, JSON payloads, JSON Schema validation.
- Sample REST API in docker compose.

## Phase 3: MongoDB Database Testing

- pymongo client layer with per-test data seeding and teardown.
- Document and collection assertion helpers.
- MongoDB in docker compose.
- Full-stack scenario: UI action, API effect, database state verification.
