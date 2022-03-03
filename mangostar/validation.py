from loguru import logger


def is_materialized_view(bucket: str, tags: dict = {}) -> bool:
    logger.info(
        f"Searching for the materialized view. Bucket: {bucket}, tags: {tags}"
    )
    return False


def is_schema_different(schemas: dict, materialized_hash: str) -> bool:
    logger.info(f"Checking to see if the schemas are different.")
    return False
