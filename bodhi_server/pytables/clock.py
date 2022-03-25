from .imports import *

Clock = Table(
    "clock",
    metadata,
    Column(
        "id",
        UUID(as_uuid = True),
        default = uuid.uuid4(),
        primary_key = True,
        unique = True,
        nullable = False
    ),
    Column("step_size", NUMERIC, default = 1, nullable = False),
    Column("window_size", Integer, default = 1, nullable = False),
    Column('head', Timestampz, nullable = False),
    Column('tail', Timestampz, nullable = False),
    Column("y_size", Integer, default = 1, nullable = False),
    Column('y_pred', Timestampz(), nullable = False),
)