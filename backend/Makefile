.PHONY: up down logs migrate superuser test

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose run --rm backend python manage.py migrate

superuser:
	docker compose run --rm -it backend python manage.py createsuperuser

test:
	docker compose run --rm -e CELERY_TASK_ALWAYS_EAGER=1 backend python -m pytest tests/ -v --tb=short
