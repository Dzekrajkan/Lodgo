.PHONY: setup demo up down logs test shell

# Copy all example env files
setup:
	cp example.env .env
	cp backend/example.env backend/.env
	cp frontend/example.env frontend/.env

# Demo (quick start)
demo:
	docker compose -f docker-compose.demo.yml up --build

# Production
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

# Run tests
test:
	pytest

# Open shell inside backend container
shell:
	docker compose exec backend sh