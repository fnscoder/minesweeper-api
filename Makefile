build:
	docker compose build --no-cache

up:
	docker compose up

upd:
	docker compose up -d

migrate:
	docker compose run app python manage.py migrate

makemigrations:
	docker compose run app python manage.py makemigrations

stop:
	docker compose stop

test:
	docker compose run app python manage.py test

statics:
	docker compose run app python manage.py collectstatic

createsuperuser:
	docker compose run app python manage.py createsuperuser

bash:
	docker compose run app bash

lint:
	docker compose run app ruff check .

format:
	docker compose run app ruff format .

help:
	@echo "  Makefile options"
	@echo "  |"
	@echo "  |_ help (default)          - Show this message"
	@echo "  |"
	@echo "  |_ build                   - Build the docker image"
	@echo "  |_ up                      - Run the project with compose"
	@echo "  |_ upd                     - Run the project with compose and -d option"
	@echo "  |_ migrate                 - Run migrations"
	@echo "  |_ makemigrations          - Create migrations"
	@echo "  |_ stop                    - Stop the docker containers"
	@echo "  |_ test                    - Run the tests"
	@echo "  |_ statics                 - Collect statics (useful to use the admin site)"
	@echo "  |_ createsuperuser         - Create super user to access the admin"
	@echo "  |_ bash                    - Run the bash inside the container"
	@echo "  |_ lint                    - Check lint with RUFF"
	@echo "  |_ format                  - Format the code with RUFF"