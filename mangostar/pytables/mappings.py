from .imports import *

Mappings = Table(
    "mappings",
    metadata,
    Column(
        "id", UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
    ),
    Column("key_name", String, default=1, nullable=False),
    Column("key_id", String, nullable=False),
    Column("value_name", String, default=1, nullable=False),
    Column('value_type', String, nullable=False),
)
