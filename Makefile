SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete

test:
	uv run backend/manage.py test backend/ $(ARG) --parallel --keepdb

test_reset:
	uv run backend/manage.py test backend/ $(ARG) --parallel

backend_format:
	uv run ruff format backend

# Commands for Docker version
docker_setup:
	docker volume create {{project_name}}_dbdata
	docker compose build --no-cache backend
	docker compose run --rm backend python manage.py spectacular --color --file schema.yml
	docker compose run frontend pnpm install
	docker compose run --rm frontend pnpm run openapi-ts

docker_test:
	docker compose run backend python manage.py test $(ARG) --parallel --keepdb

docker_test_reset:
	docker compose run backend python manage.py test $(ARG) --parallel

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
	docker compose run --rm backend python manage.py spectacular --color --file schema.yml

docker_frontend_update_api:
	docker compose run --rm frontend pnpm run openapi-ts

docker_generate_client: docker_backend_update_schema docker_frontend_update_api

docker_fresh_db:
	docker compose run --rm backend python manage.py flush --no-input
	docker compose run --rm backend python manage.py migrate

docker_createsuperuser:
	docker compose run --rm backend python manage.py createsuperuser

# Local development commands (non-Docker)
install:
	cd backend && uv sync
	cd frontend && pnpm install

install_backend:
	cd backend && uv sync

install_frontend:
	cd frontend && pnpm install

run_backend:
	cd backend && uv run python manage.py runserver

run_frontend:
	cd frontend && pnpm run dev

run:
	$(MAKE) -j2 run_backend run_frontend

migrate:
	cd backend && uv run python manage.py migrate

makemigrations:
	cd backend && uv run python manage.py makemigrations

createsuperuser:
	cd backend && uv run python manage.py createsuperuser

generate_schema:
	cd backend && uv run python manage.py spectacular --color --file schema.yml

generate_client: generate_schema
	cd frontend && pnpm run openapi-ts

fresh_db:
	cd backend && uv run python manage.py flush --no-input
	cd backend && uv run python manage.py migrate

lint_backend:
	uv run ruff check backend/
	uv run ruff format backend/ --check

lint_frontend:
	cd frontend && pnpm run lint

lint:
	$(MAKE) lint_backend
	$(MAKE) lint_frontend

format:
	uv run ruff format backend/
	cd frontend && pnpm run lint --apply
