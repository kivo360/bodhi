from typing import Tuple

from loguru import logger

from bodhi_server.graph_database.graph import *
from bodhi_server.graph_database.utilz import dict_to_schema
from bodhi_server.logic.interfaces import NamespaceResponse

"""
    Isolating the logic for this piece. 
    
    The namespace maestro will incorporate these to interact with the schema.
    
    # NOTE: Will encorporate the quantumleap api later for pipeline generation. 
        # It will require an entity-attr-metadata graph to be computed and stored like we already have in networkx.
        # It could be possible to use the notification interface they have to manage feature management.
"""


def add_schema(item: dict, ns_resp: NamespaceResponse) -> str:
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
    entry = dict_to_schema(item, check=True)
    schema_node = SchemaSpot(project="bodhi", schema_def=entry)
    gcomm.add_node(vnn)

    return ""


def create_view(ns_resp: NamespaceResponse) -> bool:
    """Send a command to update the schema inside of the database (one for now).

    Args:
        ns_resp (NamespaceResponse): The information we're using to relocate the schema again.

    Returns:
        bool: True if we were able to successfully send a create view command. View should overwrite existing one.
    """


def merge_schema(*, item: dict, ns_resp: NamespaceResponse):
    """## Merge two schemas together and add the schema into the the database. A complete overwrite is in order.

    Args:
        ns_resp (NamespaceResponse): The information we're using to relocate the schema again.

    Returns:
        bool: [description]

    ### Steps
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
