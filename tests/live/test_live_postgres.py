import time
import uuid

import pytest

from mangostar.commands import ingest_data


@pytest.mark.living
def test_send_insert():
    data_dict = {
        "id": 1,
        "first_name": "Elsbeth",
        "last_name": "Grioli",
        "email": "egrioli0@example.com",
        "gender": "Non-binary",
        "ip_address": "43.141.42.230"
    }
    ingestion_input = {
        "bucket": "person_test",
        "data": data_dict,
        "event_at": time.time(),
        "tags": {
            "client_id": uuid.uuid4().hex
        }
    }
    ingest_data(**ingestion_input)
