from .imports import *

Episode = Table(
    "episode",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column('start', Timestampz, nullable=False),
    Column('end', Timestampz, nullable=False),
    Column("is_finished", Integer, default=1, nullable=False),
)