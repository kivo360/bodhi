import os

from loguru import logger

import respx
from httpx import Response

from mangostar.clients.faas import FaaSClient

test_host = "example.com"
test_port = 5050
test_protocol = "https"
os.environ['GATEWAY_PORT'] = str(test_port)
os.environ['GATEWAY_HOST'] = test_host
os.environ['GATEWAY_PROTO'] = test_protocol


class MockedAPIMixin:
    @classmethod
    def setup_class(cls):
        logger.critical(os.environ["GATEWAY_PORT"])
        cls.mocked_api = respx.mock(
            base_url = f"{test_protocol}://{test_host}:{test_port}",
            assert_all_called = False
        )
        cls.faas_client = FaaSClient()
        insert_route = cls.mocked_api.post(
            "/function/insert", name = "insert_route"
        )
        query_route = cls.mocked_api.post(
            "/function/query", name = "query_route"
        )
        delete_route = cls.mocked_api.post(
            "/function/delete", name = "delete_route"
        )
        insert_route.return_value = Response(200, json = [])
        query_route.return_value = Response(200, json = [])
        delete_route.return_value = Response(200, json = [])

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.mocked_api.start()

    def teardown_method(self, method):
        self.mocked_api.stop()

    def teardown_class(cls):
        pass


class TestFaasClient(MockedAPIMixin):
    def test_call_insert(self):
        self.faas_client(name = 'insert')
        route = self.mocked_api["insert_route"]
        last_response: Response = route.calls.last.response
        assert route.called
        assert last_response.status_code == 200

    def test_call_query(self):
        self.faas_client(name = 'query')
        route = self.mocked_api["query_route"]
        last_response: Response = route.calls.last.response
        assert route.called
        assert last_response.status_code == 200

    def test_call_delete(self):
        self.faas_client(name = 'delete')
        route = self.mocked_api["delete_route"]
        last_response: Response = route.calls.last.response
        assert route.called
        assert last_response.status_code == 200
