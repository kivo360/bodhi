build:
	docker-compose build

up-db:
	docker-compose up -d postgres-db arango-db postgrest
	

build-dev:
	docker-compose build
	docker-compose run --rm web python manage.py migrate
	docker-compose up web

debug:
	python ./manage.py runserver

test-dev:
	watchexec -c -e py -r pytest

migrate:
	python manage.py makemigrations
	python manage.py migrate

down-db:
	docker-compose down
	docker volume prune

purge-vol:
	docker volume prune
	fd -p -g '**/**/migrations/**/*.{py,pyc}' -E __init__.py -x rm -rf

dj-run:
	python manage.py runserver

dj-super:
	python manage.py createsuperuser

demigrate:
	fd -p -g '**/**/migrations/**/*.{py,pyc}' -E __init__.py -x rm -rf
	python manage.py makemigrations
	python manage.py migrate --fake rtserver zero

djnotebook:
	python manage.py shell_plus --notebook



superuser:
	python manage.py createsuperuser

dj-user:
	python manage.py createuser

dj-shell:
	python manage.py shell

or-deploy:
	prefect deployment create ./server/orion.py

or-serve:
	prefect orion start

or-reset:
	prefect orion database reset -y
