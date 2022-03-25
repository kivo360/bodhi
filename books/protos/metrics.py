from datetime import datetime, timedelta
import time
import random as rand
import uuid
from loguru import logger

from bodhi_server import circular as circle, models, utils, connection


def save_metric():
    tbl = circle.init()
    hatch = rand.uniform(18910000.0, 38910000.0)
    data_dict = {
        "pool_balance": 1,
        "slippage": 0.044,
        "raise_hatch": hatch,
        "exit_tribute": hatch * 0.3,
        "community_funds": hatch * 0.4,
    }
    curr_time = datetime.now()
    ingestion_input = {
        "subject": "augmented_dao",
        "data": data_dict,
        "clock_at": (curr_time + timedelta(minutes=10)).timestamp(),
        "created_at": curr_time.timestamp(),
        "tags": {"client_id": uuid.uuid4().hex},
    }

    tags = ingestion_input.pop("tags", {})
    clock_at = ingestion_input.get("clock_at", time.time())
    created_at = ingestion_input.get("created_at", time.time())
    subject = ingestion_input.get("subject")

    _metrics = ingestion_input.get("data", {})
    if not _metrics:
        raise AttributeError("The ingested data needs metrics")

    logger.warning(tags)
    logger.debug(clock_at)
    logger.success(created_at)
    logger.error(subject)
    measure_batch = []
    for key, val in _metrics.items():

        measure = models.Measurement(
            name=key,
            value=val,
            tags=tags,
            dtype=type(val).__name__,
            subject=subject,
            clock_at=clock_at,
            created_at=created_at,
        )
        logger.debug(measure.processed())
        measure_batch.append(measure.processed())

    tbl.metrics.insert_many(measure_batch)


# save_metric()
def main():
    save_metric()


if __name__ == "__main__":
    main()
