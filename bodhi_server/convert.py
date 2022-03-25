from bodhi_server import system
from bodhi_server.graph_database.utilz import dict_to_schema
from bodhi_server.relational import plan_sql
from bodhi_server.walkers import schema_walk


def json_to_sql(json_record: dict, root_table_name: str):
    json_record_schema = dict_to_schema(item=json_record, check=True)
    schema_walk(json_record_schema, root_table_name)
    global_system = system()
    created_views = plan_sql(global_system)
    return created_views


if __name__ == "__main__":
    json_to_sql({"hello": "world", "eat": {"tons": "of shit"}}, "playground")
