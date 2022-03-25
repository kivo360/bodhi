from sqlalchemy import func

from .imports import *

Unstructured = Table(
    'unstructured',
    metadata,
    Column(
        "id",
        UUID(as_uuid = True),
        default = uuid.uuid4(),
        primary_key = True,
        unique = True,
        nullable = False
    ),
    Column('data', JSONB, default = {}),
    Column('tags', JSONB, default = {}),
    Column('bucket', TEXT, nullable = False),
    Column('reference_time', Timestampz, nullable = False),
    Column('insert_time', Timestampz, nullable = False)
)
