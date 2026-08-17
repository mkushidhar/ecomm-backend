# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Async FastAPI + SQLAlchemy 2.0 (`asyncmy`/MySQL 8.4) on Python 3.14, managed by `uv`. Alembic for migrations. All tooling runs through `uv run`; the `Makefile` is the intended entrypoint.

## Commands

```bash
make install        # uv sync
make run            # uv run fastapi dev  (entrypoint from [tool.fastapi]: ecomm.main:app)
make check          # pre-commit --all-files + pytest — mirrors CI exactly; run before pushing
make lint           # ruff check
make format         # ruff format (rewrites)
make typecheck      # mypy, strict = true
make test           # pytest (coverage is always on via addopts)
make precommit      # install the git hook (do this once per clone)
```

Single test: `uv run pytest tests/test_main.py::test_root_returns_status_working`
Skip coverage noise: `uv run pytest -p no:cacheprovider --no-cov <target>`

Docker (`app` + `db` compose services): `make docker-up`, `make docker-down`, `make docker-clean`, `make docker-migrate`.

Migrations: `make migration name="add foo"` (autogenerate), `make migrate` (upgrade head), `make migrate-down`, `make migrate-check` (fails on model/migration drift), `make migrate-history`.

## Configuration — read this before running anything

`Settings()` is instantiated at import time in `src/ecomm/core/config.py`, so `DB_NAME`, `DB_USER`, and `DB_PASSWORD` **must** be present or *any* import of that module explodes — including pytest collection and Alembic. A `.env` file is required; CI does `cp .env.example .env`.

`DB_HOST` defaults to `db`, the compose service name. Running the app natively on the host requires overriding `DB_HOST=localhost` (or setting `DATABASE_URL`, which short-circuits the whole `DB_*` composition in `resolved_database_url`).

## Alembic layout (non-obvious)

- Alembic config lives in **`pyproject.toml` under `[tool.alembic]`** (new-style, Alembic ≥1.19). `alembic.ini` only carries logging config; its `sqlalchemy.url` placeholder is dead — `migrations/env.py` calls `settings.resolved_database_url` so the app and migrations can never disagree on the DB URL.
- **A new model must be imported in `migrations/env.py`** to register itself on `Base.metadata`. Otherwise autogenerate sees no table and will happily emit a migration that drops it.
- `env.py` runs online migrations through an async engine (`asyncio.run` → `create_async_engine`) with `compare_type` and `compare_server_default` enabled.
- Post-write hooks in `pyproject.toml` run `ruff check --fix` and `ruff format` on every generated revision, so generated files come out already conforming.

## Architecture

`src/` layout, package `ecomm`, built with `uv_build`.

- `core/` — shared infrastructure: `config.py` (pydantic-settings singleton `settings`), `base.py` (the single `DeclarativeBase` subclass `Base`), `database.py` (module-level `engine`, `async_session_factory`, and the `get_db` async-generator dependency).
- `main.py` — creates `app`, includes each feature router.
- Feature packages (`products/` is the template): `models.py` (SQLAlchemy), `schemas.py` (Pydantic request/response), `<feature>.py` (the `APIRouter`), and `__init__.py` re-exporting the router under a namespaced alias (`product_router`). New features follow this shape and get wired into `main.py`.
- `health.py` sits at the top level (not yet a package) and owns `/api/v1/health`.

Conventions that recur:

- Routers declare their own DB dependency alias: `DbConn = Annotated[AsyncSession, Depends(get_db)]`.
- The session factory sets `expire_on_commit=False` and `autoflush=False`, so server-generated values need an explicit `await db.refresh(obj)` after `commit()`.
- Routes carry explicit return type annotations plus `response_model`/`status_code` — mypy strict means every function is annotated.

## Testing state

`tests/` has no `conftest.py`, no `TestClient`, and no DB fixtures yet — the one existing test calls a route function directly. Anything touching `get_db` needs that fixture scaffolding built first. Coverage gate is `fail_under = 0` on purpose ("update later").

## Known gaps (deliberate, not oversights)

No service/repository layer — routers hold controller + persistence logic inline. No global exception handlers, no try/except around commits, and no logging setup anywhere in the app.
