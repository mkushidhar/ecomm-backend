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
- **A new model must be imported in `migrations/env.py`** to register itself on `Base.metadata`. Otherwise autogenerate sees no table and will happily emit a migration that drops it. Import it from its own module (`from ecomm.products.models import Product`), never via a package re-export — routing it through `__init__.py` means a later tidy of that file silently empties the metadata, and the resulting migration is a `DROP TABLE`. `make migrate-check` (`alembic check`) catches this, but it is **not** wired into CI (CI has no database service).
- `env.py` runs online migrations through an async engine (`asyncio.run` → `create_async_engine`) with `compare_type` and `compare_server_default` enabled.
- Post-write hooks in `pyproject.toml` run `ruff check --fix` and `ruff format` on every generated revision, so generated files come out already conforming.

## Architecture

`src/` layout, package `ecomm`, built with `uv_build`.

- `core/` — shared infrastructure: `config.py` (pydantic-settings singleton `settings`), `base.py` (the single `DeclarativeBase` subclass `Base`), `database.py` (module-level `engine`, `async_session_factory`, and the `get_db` async-generator dependency).
- `main.py` — creates `app`, includes each feature router.
- Feature packages (`products/` is the template) are layered, one role per module: `models.py` (SQLAlchemy), `schemas.py` (Pydantic request/response/query), `repository.py` (data access; holds the `AsyncSession`), `service.py` (orchestration; holds a repository), `deps.py` (wires the two into a `Depends` alias), `router.py` (the `APIRouter`), and `__init__.py` re-exporting *only* the router under a namespaced alias (`product_router`). New features follow this shape and get wired into `main.py`.
- `health.py` sits at the top level (not yet a package) and owns `/api/v1/health`.

Conventions that recur:

- `DbConn = Annotated[AsyncSession, Depends(get_db)]` is declared once, in `core/database.py`, and imported — do not re-declare it per router. Feature packages stack their own alias on top in `deps.py` (`ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]`); routers depend on *that*, not on `DbConn`. Only `health.py` uses `DbConn` directly, because it has no service layer.
- Literal paths must be registered before parameterized ones — `GET /list` is declared above `GET /{id}` in `products/router.py`, otherwise FastAPI matches `/{id}` first and 422s on `"list"` as a `UUID`.
- The session factory sets `expire_on_commit=False` and `autoflush=False`, so server-generated values need an explicit `await db.refresh(obj)` after `commit()`.
- Routes carry explicit return type annotations plus `response_model`/`status_code` — mypy strict means every function is annotated.

## Testing state

`tests/` has no `conftest.py`, no `TestClient`, and no DB fixtures yet — the one existing test calls a route function directly. Anything touching `get_db` needs that fixture scaffolding built first. Coverage gate is `fail_under = 0` on purpose ("update later").

## Known gaps (deliberate, not oversights)

No global exception handlers, no try/except around commits, and no logging setup anywhere in the app. `health.py` is still a top-level module rather than a package, and reaches for the session directly instead of going through a service.
