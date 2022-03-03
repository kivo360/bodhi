from mangostar import system
from mangostar import System
from mangostar.walkers import schema_walk


def test_jsonschema_to_graph(nested_jsonschema: dict):
    schema_walk(nested_jsonschema, name = "root_system")
    global_system: System = system()

    global_system_dict = global_system.to_dict()
    relationships = list(
        filter(lambda x: "adjacencies" in x, global_system_dict)
    )
    rel_num = len(relationships)
    assert rel_num > 0
    assert rel_num == 8
