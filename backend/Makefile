.PHONY: up down logs migrate superuser

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
