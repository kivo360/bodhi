from unittest.mock import MagicMock
from unittest.mock import patch

from devtools import debug

from faker import Faker

from bodhi_server import connection
from bodhi_server.graph_database.utilz import gen_hex_id
from bodhi_server.graph_database.utilz import is_json_schema
from bodhi_server.logic.interfaces import NamespaceResponse
from bodhi_server.logic.maestro import NameMaestro
from bodhi_server.settings import ModuleSettings


modset = ModuleSettings()


def create_profile():
    origin_dict = {
        "id": 1,
        "first_name": "Elsbeth",
        "last_name": "Grioli",
        "email": "egrioli0@example.com",
        "gender": "Non-binary",
        "ip_address": "43.141.42.230",
    }
    return origin_dict


def test_dict_to_schema():
    origin_dict = {
        "id": 1,
        "first_name": "Elsbeth",
        "last_name": "Grioli",
        "email": "egrioli0@example.com",
        "gender": "Non-binary",
        "ip_address": "43.141.42.230",
    }
    is_schema, should_continue = is_json_schema(origin_dict)
    assert should_continue
    assert not is_schema


class TestSchemaManagement:
    def setup_class(self):
        self.master = NameMaestro()
        self.fake = Faker()

    def teardown_class(self):
        print("teardown_class called once for the class")

    def test_user_doesnt_exist(self):

        resp = self.master.get_or_create_namespace_view(
            view_name=gen_hex_id(), **modset.ns_dict
        )
        assert not resp.is_prior
        assert not resp.is_schema

    @patch("bodhi_server.logic.maestro.NameMaestro.create_view")
    @patch("bodhi_server.logic.maestro.NameMaestro.add_schema")
    def test_updae_schema_not_prior(self, schema_mock: MagicMock, view_mock: MagicMock):
        profile: dict = create_profile()
        default_response = NamespaceResponse()
        self.master._update_schema(item=profile, namespace_response=default_response)
        schema_mock.assert_called_once_with(item=profile, ns_resp=default_response)
        view_mock.assert_called_once_with(default_response)

    @patch("bodhi_server.logic.maestro.NameMaestro.merge_schema")
    @patch("bodhi_server.logic.maestro.NameMaestro.create_view")
    @patch("bodhi_server.logic.maestro.NameMaestro.add_schema")
    # create_view
    def test_update_schema_is_schema(
        self,
        schema_mock: MagicMock,
        view_mock: MagicMock,
        merge_mock: MagicMock,
    ):
        profile: dict = create_profile()
        default_response = NamespaceResponse(is_prior=True, schema_hash=gen_hex_id())
        self.master._update_schema(item=profile, namespace_response=default_response)

        schema_mock.assert_not_called()
        # view_mock.assert_not_called()
        merge_mock.assert_called()
