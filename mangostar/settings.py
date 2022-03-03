import os
from typing import Dict, Optional, Tuple

from devtools import debug

from addict import Dict as Add
from faker import Faker
from pydantic import BaseSettings
from pydantic import Field
from pydantic import PostgresDsn
from pydantic import root_validator
from pydantic.env_settings import SettingsSourceCallable


fake = Faker()


class EnvPrioritySettings(BaseSettings):
    class Config:
        case_sensitive = False
        env_file = ".env"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, file_secret_settings, init_settings


def pg_connection_str(
    *,
    user: str,
    host: str = "localhost",
    password: Optional[str] = None,
    port: int = 5432,
    database: Optional[str] = None,
):
    return PostgresDsn.build(
        scheme="postgresql",
        user=user,
        host=host,
        password=password,
        port=str(port),
        path=f"/{database}",
    )


class PostgresSettings(EnvPrioritySettings):
    user: Optional[str] = Field("starboy", env="PG_USER")
    password: Optional[str] = Field("", env="PG_PASSWORD")
    database: Optional[str] = Field("test", env="PG_DATABASE")
    port: Optional[int] = Field(5432, env="PG_PORT")
    host: Optional[str] = Field("localhost", env="PG_HOST")

    @property
    def connstr(self) -> str:
        return pg_connection_str(
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            host=self.host,
        )


class K8SInternalBase(EnvPrioritySettings):
    """
    Has the basic structure for all internal K8s services.
    Can override the environment variable settings using the `Config` option (`env`). It's encouraged.
    The only two variables we need to set are service_name and namespace (is default otherwise).

    Logic for developer will see:

    >> from util_lib import K8SInternalBase
    >>
    >>
    >> class CrateDBInternal(K8SInternalBase):
    >>     alts = {
    >>                "namespace": CRATEDB_NAME,
    >>                "service_name": CRATEDB_SERVICE
    >>     }
    >>
    >>


    crate_conn_str = CrateDBInternal()



    """

    service_name: str = ""
    namespace: str = "default"
    alts: Dict[str, str] = {}

    @root_validator
    def post_environment_check(cls, values: dict):
        local_values = Add(**values)
        alt_envs = local_values.alts
        # We return just the values if we haven't added any environment variables in the alts field.
        if not alt_envs:
            return values

        # Temporarily getting a shorthand.
        name_env = alt_envs.namespace
        if bool(name_env):

            name_env = str(name_env)
            local_values.namespace = (
                os.getenv(name_env.upper(), None)
                or os.getenv(name_env.lower(), None)
                or "default"
            )

        srv_env_name: str = alt_envs.service_name

        if bool(srv_env_name):
            service_env = os.getenv(srv_env_name.upper(), None) or os.getenv(
                srv_env_name.lower(), None
            )

            if service_env is None and not local_values.service_name:
                raise AttributeError("The set service env was not found anywhere.")

            if service_env:
                local_values.service_name = service_env

        debug(local_values)
        return local_values.to_dict()

    def __repr__(self) -> str:
        parent_repr = super().__repr__()
        cls_name = self.__class__.__name__
        return f"{cls_name}({parent_repr}, full_url={self.__str__()})"

    def __str__(self) -> str:
        if not self.service_name:
            raise AttributeError("You didn't specify a service name.")
        return f"{self.service_name}.{self.namespace}.svc.cluster.local"


class NamespaceSettings(EnvPrioritySettings):

    username: Optional[str] = Field("starboy", env="BODHI_USERNAME")
    stakeholder: Optional[str] = Field("supabad", env="BODHI_STAKEHOLDER")
    project: Optional[str] = Field("badbois", env="BODHI_PROJECT")


class ArangoSettings(EnvPrioritySettings):
    scheme: Optional[str] = Field("https", env="ARANOGO_SCHEME")
    host: Optional[str] = Field("localhost", env="ARANOGO_HOST")
    port: Optional[int] = Field(8529, env="ARANOGO_PORT")
    database: Optional[str] = Field("test", env="ARANOGO_DATABASE")
    user: Optional[str] = Field("root", env="ARANOGO_USER")
    password: Optional[str] = Field("8uLiSAXHM0g7t1Hjoo27", env="ARANOGO_PASSWORD")
    graph_name: Optional[str] = Field(
        default_factory=lambda: fake.cryptocurrency_name(), env="ARANOGO_GRAPH_NAME"
    )

    @property
    def url(self):
        return f"{self.scheme}://{self.host}:{self.port}"


class APIKeys(EnvPrioritySettings):
    news_api: str = Field(..., env="NEWSAPI_KEY")


class ModuleSettings:
    def __init__(self):
        # pass
        self.postgres: PostgresSettings = PostgresSettings()
        self.arangoo: ArangoSettings = ArangoSettings()
        self.namespace: NamespaceSettings = NamespaceSettings()

    @property
    def postgres_connection_str(self) -> PostgresDsn:
        return self.postgres.connstr

    @property
    def arango_host(self) -> str:
        return self.arangoo.url

    @property
    def ns_dict(self):
        return self.namespace.dict()

    def __repr__(self):
        return f"{repr(self.postgres)}\n\n{repr(self.arangoo)}"
