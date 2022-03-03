from .imports import *

Sessions = Table(
    "sessions",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("num_episodes", Integer, default=0, nullable=False),
    Column('is_finished', Boolean, default=False, nullable=False),
)