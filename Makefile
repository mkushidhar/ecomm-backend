.PHONY: help install lint format format-check typecheck test precommit precommit-run check run clean \
	docker-build docker-up docker-down docker-clean

help:
	@echo "install        Install/sync dependencies (uv sync)"
	@echo "lint           Run ruff check"
	@echo "format         Run ruff format (rewrites files)"
	@echo "format-check   Check formatting without rewriting files"
	@echo "typecheck      Run mypy (strict)"
	@echo "test           Run pytest"
	@echo "precommit      Install the pre-commit git hook"
	@echo "precommit-run  Run all pre-commit hooks against the whole repo"
	@echo "check          precommit-run + test (mirrors CI exactly)"
	@echo "run            Run the FastAPI dev server (reload enabled)"
	@echo "clean          Remove caches and build artifacts"
	@echo "docker-build   Build the dev container image"
	@echo "docker-up      Start the dev container (foreground, reload enabled)"
	@echo "docker-down    Stop and remove the dev container"
	@echo "docker-clean   docker-down plus remove volumes/orphans"

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy .

test:
	uv run pytest

precommit:
	uv run pre-commit install

precommit-run:
	uv run pre-commit run --all-files

check: precommit-run test

run:
	uv run fastapi dev

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-clean:
	docker compose down --volumes --remove-orphans
