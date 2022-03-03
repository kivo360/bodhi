import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy import MetaData

from mangostar import connection
from mangostar.tables import MetaTableAdapter
from mangostar.tables import select
from mangostar.utils import execute


class TestTimeCrudOperations:
    def setup_class(cls):
        engine = create_engine(connection.settings.postgres_connection_str)
        metadata = MetaData(bind = engine)
        cls.adapter = MetaTableAdapter(metadata)
        # Create table
        cls.metadata = metadata
        cls.engine = engine
        # You're hopefully running this on a test database
        # cls.metadata.drop_all()
        time.sleep(2)
        cls.metadata.create_all()
        cls.kernel = cls.adapter.kernel

    @pytest.mark.skip("Skipping this test. Depreciated.")
    def test_insert_json_record(self):
        # print("hello_world")
        ex = execute(engine = self.engine)
        self.kernel.insert_into(
            is_execute = True,
            bucket = "token",
            data = {"key": "value_pair"},
        )
        (
            ex(
                self.kernel.insert_into(
                    bucket = "token",
                    data = {"key": "value_pair"},
                )
            )
        )
        select_results = ex(select(self.kernel))
        assert select_results.rowcount == 1

    # def test_create_materialized_view(self):
    #     assert True

    # def test_drop_materialized_view(self):
    #     pass

    # def test_query_materialized_view(self):
    #     pass

    # def teardown_class(cls):
    #     cls.metadata.drop_all()
