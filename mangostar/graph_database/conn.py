from loguru import logger

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import DatabaseCreateError
from arango.exceptions import UserCreateError
from retry import retry

from mangostar.settings import ModuleSettings


# mod_set = ModuleSettings()


class GraphConnection:
    settings: ModuleSettings = ModuleSettings()

    def __init__(self):
        # These are guarunteed to work. So we're keeping these.
        self.client = ArangoClient(hosts=self.settings.arango_host)
        self._system = self.client.db(
            "_system", username="root", password=self.settings.arangoo.password
        )
        self.desired: StandardDatabase = None

    @retry(delay=0.2, backoff=0.5, max_delay=1.5)
    def create_database(self):
        if not self._system.has_database(self.settings.arangoo.database):
            self._system.create_database(
                self.settings.arangoo.database,
                [
                    {
                        "username": self.settings.arangoo.user,
                        "password": self.settings.arangoo.password,
                        "active": True,
                        "extra": {"Department": "IT"},
                    }
                ],
                replication_factor=3,
            )

    @retry(delay=0.2, backoff=0.5, max_delay=1.5)
    def create_user(self):
        if not self._system.has_user(self.settings.arangoo.user):
            self._system.create_user(
                username=self.settings.arangoo.user,
                password=self.settings.arangoo.password,
                active=True,
                extra={"team": "testers", "title": "engineer"},
            )

    @retry(delay=0.2, backoff=0.5, max_delay=1.5)
    def update_permissions(self):
        permissions = self._system.permissions(self.settings.arangoo.user)
        is_perm = self._system.update_permission(
            username=self.settings.arangoo.user,
            database=self.settings.arangoo.database,
            permission="rw",
        )
        is_perm
        permissions

    def get_database(self, run_steps: bool = True):
        """
        Here we get the database by the environment variable set.
        """
        if not run_steps:
            return self.client.db(self.settings.arangoo.database)

        self.create_user()
        self.create_database()
        self.update_permissions()
        return self.client.db(
            name=self.settings.arangoo.database,
            username=self.settings.arangoo.user,
            password=self.settings.arangoo.password,
        )
