"""create anon

Revision ID: e79e6b5bb56b
Revises: 3b3290cc44cc
Create Date: 2022-02-27 07:11:24.597469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e79e6b5bb56b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    DB_ANON_ROLE = 'anon'
    DB_SCHEMA = "public"
    schema = f"""
    CREATE USER {DB_ANON_ROLE};
    GRANT USAGE ON SCHEMA {DB_SCHEMA} TO {DB_ANON_ROLE};
    ALTER DEFAULT PRIVILEGES IN SCHEMA {DB_SCHEMA} GRANT SELECT ON TABLES TO {DB_ANON_ROLE};
    GRANT SELECT ON ALL SEQUENCES IN SCHEMA {DB_SCHEMA} TO {DB_ANON_ROLE};
    GRANT SELECT ON ALL TABLES IN SCHEMA {DB_SCHEMA} TO {DB_ANON_ROLE};
    """
    op.execute(schema)


def downgrade():
    pass
