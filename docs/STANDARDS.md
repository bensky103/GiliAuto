# Coding Standards & Protocols

## 1. Philosophy
* **Minimalism:** Do not add a library unless absolutely necessary.
* **Async First:** All I/O (DB, Network) must be `async/await`.
* **Type Safety:** 100% Type Hinting coverage.
* **English Codebase:** All comments and variable names in English. Only string literals for Monday statuses are Hebrew.

## 2. Project Structure
```text
src/
  ├── core/          # Config, Logging, Exceptions
  ├── db/            # Models, Session Manager
  ├── services/      # MondayService, MetaService, SchedulerService
  ├── routers/       # Webhook endpoints
  └── main.py        # App Entrypoint
tests/
  └── ...
scripts/
  └── start.sh

## 3. Error Handling
Webhooks: Never crash the app on a bad webhook. Log error -> Return 200 OK to provider (to stop retries) -> Alert (Log).

External APIs: Handle httpx.HTTPError gracefully.

