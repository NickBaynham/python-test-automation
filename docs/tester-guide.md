# Tester Guide

How to automate tests with this platform. Every code example in this guide
has been executed against the dockerized sample stack and shown to pass.

## 1. Introduction

This platform automates testing at three layers:

| Layer | Suite | Verifies | Built on |
|---|---|---|---|
| UI | `tests/e2e/` | What a user sees and does in the browser | Playwright, page objects |
| API | `tests/integration/` | REST contracts: status codes, payloads, schemas | httpx client, assertion helpers |
| Database | `tests/integration/` | Stored state behind the application | pymongo target, seeding, state assertions |

A fourth pattern, the full-stack scenario, chains all three: act in the UI,
verify through the API, confirm the document in MongoDB
([tests/e2e/test_full_stack.py](../tests/e2e/test_full_stack.py) is the
reference).

Prerequisites are listed in the [README](../README.md). First run:

```
make install            # dependencies
make install-browsers   # detect and install browsers, write config/browsers.json
make docker-up          # start the sample stack (app, API, MongoDB)
make test               # run everything
make report             # browse the Allure report
```

## 2. Testing at Each Layer

### 2.1 UI tests

UI tests live in `tests/e2e/` and are written against page objects, never
against raw selectors. The fixtures in `tests/e2e/conftest.py` give every
test a fresh browser page, run it across every browser marked available in
`config/browsers.json`, and capture a screenshot and trace on failure.

Step by step:

1. Create a page object under `tests/e2e/pages/` extending `BasePage`.
   Implement `path` (the route) and `ready_locator` (visible exactly when
   the page is usable). Expose locators and actions as attributes and
   methods. Locator conventions: `get_by_role` with an accessible name
   first, `get_by_test_id` where a role would be ambiguous, never
   structural CSS or XPath. See
   [tests/e2e/pages/sample_app.py](../tests/e2e/pages/sample_app.py).
2. Write the test as a plain function taking the page-object fixture.
   Use Playwright's `expect` (it waits; never `time.sleep`).
3. Create unique data and clean it up (the `track_item` fixture deletes
   tracked items through the API after the test).

Worked example (executed and passing on all available browsers):

```python
from collections.abc import Callable
from uuid import uuid4

from playwright.sync_api import expect

from tests.e2e.pages.sample_app import SampleAppPage


def test_new_item_is_listed(
    sample_app: SampleAppPage, track_item: Callable[[str], str]
) -> None:
    name = track_item(f"guide-{uuid4().hex[:8]}")
    sample_app.open()
    sample_app.add_item(name)
    expect(sample_app.items().filter(has_text=name)).to_have_count(1)
```

Run it: `make docker-up` then `make test-e2e`.

### 2.2 API tests

API tests live in `tests/integration/`. The `api` fixture provides an
`ApiClient` bound to `TP_API_BASE_URL`; assertion helpers produce failure
messages that carry the response body, so a failure is diagnosable from the
report alone.

Step by step:

1. Take the `api` fixture; call `api.get/post/request`, or build a
   declarative `ApiCall` and `api.send(call)`.
2. Assert with `assert_status`, `assert_json`, `assert_json_contains`, or
   `assert_matches_schema` (JSON Schema 2020-12; reports every violation).
3. Delete what you create.

Worked example (executed and passing):

```python
from testplatform.api import ApiClient
from testplatform.assertions import assert_json_contains, assert_status


def test_item_lifecycle(api: ApiClient) -> None:
    created = api.post("/items", json_body={"name": "guide item"})
    assert_status(created, 201)
    item_id = created.json()["id"]

    fetched = api.get(f"/items/{item_id}")
    assert_status(fetched, 200)
    assert_json_contains(fetched, {"name": "guide item"})

    assert_status(api.request("DELETE", f"/items/{item_id}"), 204)
    assert_status(api.get(f"/items/{item_id}"), 404)
```

Run it: `make docker-up` then `make test-integration`.

### 2.3 Database tests

Database tests also live in `tests/integration/`. The `mongo_target`
fixture connects to `TP_MONGO_URL` (failing fast with guidance when the
database is down); the `seeder` fixture inserts documents and removes
exactly what it seeded after the test — by id, never dropping collections.

Step by step:

1. Take `mongo_target` and `seeder`.
2. Seed the state your test needs, tagged with a unique marker so queries
   never collide with other tests' data.
3. Assert with `assert_document_exists`, `assert_document_absent`,
   `assert_field_values`, or `assert_collection_count`.

Worked example (executed and passing):

```python
from uuid import uuid4

from testplatform.assertions import assert_collection_count, assert_field_values
from testplatform.db import MongoSeeder, MongoTarget


def test_seeded_order_state(mongo_target: MongoTarget, seeder: MongoSeeder) -> None:
    tag = f"guide-{uuid4().hex[:8]}"
    seeder.seed(
        "orders", {"tag": tag, "status": "new"}, {"tag": tag, "status": "paid"}
    )
    assert_collection_count(mongo_target, "orders", 2, {"tag": tag})
    assert_field_values(
        mongo_target, "orders", {"tag": tag, "status": "paid"}, {"status": "paid"}
    )
```

### 2.4 The full-stack pattern

Chain the layers when the behavior under test spans them: act in the UI,
locate the effect through the API, verify the stored document. Keep one
scenario per journey — full-stack tests are the most expensive kind, so
each must earn its place. The reference implementation is
[tests/e2e/test_full_stack.py](../tests/e2e/test_full_stack.py).

## 3. Designing Tests for the Framework

**Choose the lowest layer that proves the behavior.** A payload contract
belongs in an API test, not behind a browser; a stored side effect belongs
in a database assertion; a user journey belongs in the UI suite. UI tests
verify what users experience, not what APIs return.

**Isolation is non-negotiable.** Every test creates its own data with
unique names or markers, cleans up what it creates (use `seeder` and
`track_item` — both clean up even when the test fails), and never depends
on another test having run. Whole-collection or whole-list equality
assertions are forbidden against shared state; filter to your own data.

**Settle before absence.** Never assert only that something is absent —
absence checks pass before the application reacts. Anchor on a positive
state change first, then assert the absence alongside it.

**Page objects own locators and actions; tests own assertions.** If a test
reaches for `page.get_by_*` directly, the locator belongs in a page object.
If a page object asserts, that judgment belongs in the test.

**Configuration comes from the environment.** Tests read targets through
`load_settings()`, never hardcoded URLs. Local overrides go in `.env`
(copy `.env.example`); remote targets are explicit:
`TP_TARGET_MODE=remote` with every `TP_*_URL` set. Secrets only ever come
from environment variables.

**Structure and naming.** One test file per feature area; test names state
the expected behavior (`test_added_item_appears_and_input_clears`), not
the mechanics. New platform code (clients, helpers) is developed
test-first under `tests/unit/` and must keep the coverage gate.

## 4. Troubleshooting

**"sample API not reachable ... start the stack with make docker-up"** or
**"MongoDB not reachable ..."** — the dockerized stack is down. Run
`make docker-up` and wait for all services to report healthy.

**Every e2e test skipped: "no usable browser inventory"** — missing or
invalid `config/browsers.json`. Run `make install-browsers`.

**Coverage failure when running a single test file** — the 90% gate is
calibrated for the full suite. Use `--no-cov` for spot runs:
`pdm run pytest tests/unit/test_config.py --no-cov`.

**ValidationError naming `TP_UI_BASE_URL`, `TP_API_BASE_URL`, or
`TP_MONGO_URL`** — remote target mode refuses defaulted localhost URLs.
Set every named variable explicitly.

**`docker-up` fails: "port is already allocated"** — another process owns
3100, 8100, or 27100. Copy `.env.example` to `.env` and change the port
pair (the compose port and its matching `TP_*` URL) together.

**"response body is not JSON: <html>..."** — the API base URL points at
something that is not the API (wrong port, a proxy error page). Check
`TP_API_BASE_URL` against the running stack.

**A test failed — where is the evidence?** E2e failures write a full-page
screenshot and a Playwright trace to `test-artifacts/` (named after the
test); open traces with `pdm run playwright show-trace <file>.zip`. Every
run also emits Allure results; `make report` opens the HTML report. In CI,
both are downloadable build artifacts.

**`make lint` fails on formatting** — run `make format`, which applies
formatting and safe lint fixes.

**Windows: `make` not found** — install GNU Make 4.x (`choco install
make`). All targets run natively on Windows; Docker-based suites need
Docker Desktop.
