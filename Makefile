SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete

# Local commands (uv + pnpm)
run-backend: run-openapi-schema
	cd backend && uv run python manage.py runserver 0.0.0.0:$${DJANGO_PORT:-8000}

frontend-api:
	pnpm run openapi-ts

run-frontend: frontend-api
	pnpm run dev

test:
	uv run backend/manage.py test backend/ $(ARG) --parallel --keepdb

test-verbose:
	uv run backend/manage.py test backend/ $(ARG) --parallel --keepdb --verbosity=2

test_reset:
	uv run backend/manage.py test backend/ $(ARG) --parallel

test-reset: test_reset

test-reset-verbose:
	uv run backend/manage.py test backend/ $(ARG) --parallel --verbosity=2

backend_format:
	black backend

backend-format: backend_format

lint-backend:
	uv run ruff check backend

format-backend:
	uv run ruff format backend

makemigrations:
	uv run backend/manage.py makemigrations

migrate:
	uv run backend/manage.py migrate

run-openapi-schema:
	uv run backend/manage.py export_openapi_schema --api {{project_name}}.api.api --output backend/schema.openapi

run-celery:
	uv run celery --workdir backend --app={{project_name}} worker --loglevel=info

# Docker commands
docker_setup:
	docker volume create {{project_name}}_dbdata
	docker compose build --no-cache backend frontend
	docker compose run --rm backend python manage.py export_openapi_schema --api {{project_name}}.api.api --output schema.openapi
	docker compose run --rm frontend pnpm run openapi-ts

docker_test:
	docker compose run --rm backend python manage.py test $(ARG) --parallel --keepdb

docker_test_reset:
	docker compose run --rm backend python manage.py test $(ARG) --parallel

docker_up:
	docker compose up -d

docker_update_dependencies:
	docker compose down
	docker compose up -d --build

docker_down:
	docker compose down

docker_logs:
	docker compose logs -f $(ARG)

docker_makemigrations:
	docker compose run --rm backend python manage.py makemigrations

docker_migrate:
	docker compose run --rm backend python manage.py migrate

docker_backend_shell:
	docker compose run --rm backend bash

docker_backend_update_schema:
	docker compose run --rm backend python manage.py export_openapi_schema --api {{project_name}}.api.api --output schema.openapi

docker_frontend_shell:
	docker compose run --rm frontend sh

docker_frontend_update_api:
	docker compose run --rm frontend pnpm run openapi-ts

docker_run_celery:
	docker compose run --rm backend celery --app={{project_name}} worker --loglevel=info

install-frontend:
	pnpm install

build-frontend:
	pnpm run build

lint-frontend:
	pnpm run lint

lint-frontend-fix:
	pnpm run lint:fix

format-frontend:
	pnpm run format

test-frontend:
	pnpm run test $(ARG)

test-frontend-watch:
	pnpm run test:watch

test-frontend-update:
	pnpm run test:update

tsc-frontend:
	pnpm run tsc

coverage-frontend:
	pnpm run coverage
