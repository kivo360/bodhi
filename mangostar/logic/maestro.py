from typing import Optional

from loguru import logger

from mangostar.convert import json_to_sql
from mangostar.graph_database._controller import GraphController
from mangostar.graph_database.graph import *
from mangostar.graph_database.graph import ViewNamespace
from mangostar.graph_database.utilz import *
from mangostar.logic.consts import *
from mangostar.logic.interfaces import NamespaceResponse
from mangostar.utils import *


class NameMaestro:
    def __init__(self, graph_controller: Optional[GraphController] = None):
        self.controller = graph_controller or GraphController()

    def get_or_create_namespace_view(self, view_name: str, **data):
        """Get or create namespace

        Args:
            view_name (str): The view of the namespaceself.

        Returns:
            NamespaceResponse: [description]
        """
        view_name = to_snake(view_name)
        view_ns = ViewNamespace(view_name=view_name, **data)
        # Searching for the new node here.
        accountant = self.controller.find_one_node(*view_ns.to_find())

        if accountant.is_empty:
            # You can just add what ever you please.
            self.controller.add_node(view_ns.to_node())
            return NamespaceResponse(data=data, node_acc=view_ns)
        name_res = NamespaceResponse(is_prior=True, data=data, node_acc=view_ns)
        element = accountant.element

        # Setting Specific Hashes
        eid: str = element.pop("_id", None)
        name_res.schema_hash = element.pop("schema_hash", None)
        logger.critical(name_res.schema_hash)
        name_res.prior_id = eid
        name_res.values = element
        return name_res

    def add_schema(self, item: dict, ns_resp: NamespaceResponse) -> str:
        """Add schema to a particular namespace view.

        Args:
            item (dict): The record or schema that we're adding in.
            update_id (str): The namespace view that we're adding everything into.

        Returns:
            str: The new schema ID.
        """
        # run a conversion of the item to ensure it's a jsonschema.
        # create a SchemaSpot Node
        # create a "view_of" edge.
        # TODO: Perhaps attach a database to the view node. A subscriber like pattern to create instances somewhere in the pipeline.
        schema_entry = dict_to_schema(item, check=True)
        schema_spot = SchemaSpot(
            project=ns_resp.node_acc.project, schema_def=schema_entry
        )
        schema_node = schema_spot.to_node()
        view_node = ns_resp.node_acc.to_node()

        # Creating the schema now.
        self.controller.add_node(schema_node)
        view_schema_edge = create_edge(
            SCHEMA_EDGE_NAME,
            start=schema_node,
            end=view_node,
            props={"database": CURRENT_DB_INTERFACE},
        )
        self.controller.add_edge(view_schema_edge)

        # create a hash of the schema and updating the main schema.
        updated_view_node = self.controller.update_match(
            view_node.kind, view_node.record, {"schema_hash": json_hash(schema_entry)}
        )
        return updated_view_node

    def _update_schema(self, item: dict, namespace_response: NamespaceResponse):
        is_default = not namespace_response.is_prior or not namespace_response.is_schema
        if is_default:
            self.add_schema(item=item, ns_resp=namespace_response)
            logger.info(namespace_response.schema_hash)
            return self.create_view(namespace_response)
        elif namespace_response.is_schema:
            sh_hash = schema_hash(item)
            if not namespace_response.match_hash(sh_hash):
                self.merge_schema(item=item, ns_resp=namespace_response)
                return self.create_view(namespace_response)
            return []
        else:
            raise AttributeError("There must either be a schema or an absense of one.")

    def update_schema(self, *, view_name: str, record: dict, view_space: ViewParams):
        response = self.get_or_create_namespace_view(
            view_name=view_name, **view_space.__dict__
        )
        return self._update_schema(record, response)

    def create_view(self, ns_resp: NamespaceResponse):
        # logger.debug(ns_resp)
        _node = ns_resp.node_acc.to_node()
        query = create_query(
            SCHEMA_EDGE_NAME,
            ns_resp.node_acc.to_node(),
            {"database": CURRENT_DB_INTERFACE},
        )
        schema_doc = self.controller.get_adjacent(query)
        schema = SchemaSpot(**schema_doc)
        created_views = json_to_sql(schema.schema_def, ns_resp.node_acc.view_name)
        return created_views
        # for view in created_views:
        #     logger.warning(str(view))

    def merge_schema(self, *, item: dict, ns_resp: NamespaceResponse):
        """### Merge two schemas together and add the schema into the the database. A complete overwrite is in order.

        Args:
            ns_resp (NamespaceResponse): The information we're using to relocate the schema again.

        Returns:
            bool: [description]

        #### Steps
        1. freeze the dictionary we have (with our own version of frozendict).
        2. ensure we're getting the jsonschema from the item we're adding in (should be cached if seen).
        3. get a json hash of the schema (should be cached if we've seen it already).
        4. Check if the hash matches the current hash
        5. **NOTE:** The link [here](https://github.com/wolverdude/GenSON#customizing-schemabuilder) explains how we can ensure consistency between schemas
        6. If the hash doesn't match. Merge the jsonschema together with the other.
        7. add_schema(merged_schema, namespace_response)
        8. create_view -> sends a command to create a new view.
        9. NOTE: Do it inline now, but spread to other serverless commands.
        """
        existing_schema = ns_resp.values
        existing_schema.pop("_key", None)
        existing_schema.pop("_rev", None)

        query = create_query(
            SCHEMA_EDGE_NAME,
            ns_resp.node_acc.to_node(),
            {"database": CURRENT_DB_INTERFACE},
        )

        schema_doc = self.controller.get_adjacent(query)
        record = combine_schemas(existing_schema, item)

        self.add_schema(record, ns_resp)
        # return self.create_view(ns_resp)
