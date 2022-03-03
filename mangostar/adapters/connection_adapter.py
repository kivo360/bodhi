from functools import cached_property

from arango.database import StandardDatabase
from sqlalchemy import create_engine
from sqlalchemy import MetaData

from mangostar.graph_database.conn import GraphConnection

# from mangostar import module_settings as settings
from mangostar.settings import ModuleSettings
from mangostar.tables import MetaTableAdapter


class ConnectionAdapter:
    preprocess_graph: bool = True
    settings: bool = ModuleSettings()
    _graph: StandardDatabase = None

    @property
    def graph(self):
        if not self._graph:
            self._graph = GraphConnection().get_database(self.preprocess_graph)
        return self._graph

    @cached_property
    def relational(self):
        engine = create_engine(self.settings.postgres_connection_str)
        metadata = MetaData(bind=engine)

        adapter = MetaTableAdapter(metadata)
        metadata.create_all(engine)
        return adapter
