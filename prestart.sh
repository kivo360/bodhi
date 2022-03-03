export ALEMBIC_URI="postgresql://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:5432/${POSTGRES_DB}"
alembic upgrade head
