from typing import Optional, Union

from loguru import logger

from pydantic import BaseConfig, BaseModel, Extra
from pydantic.fields import Field, FieldInfo
from pydantic.main import ModelMetaclass
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    TypeVar,
    Union,
    TYPE_CHECKING,
)
from .utils import __dataclass_transform__


# if TYPE_CHECKING:

#     from dataclasses import dataclass
# else:
from pydantic.dataclasses import dataclass

_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


@__dataclass_transform__(kw_only_default=True, field_descriptors=(Field, FieldInfo))
class ParameterMetaclass(ModelMetaclass):
    pass


class CommonConfig(BaseConfig):
    extra = Extra.allow
    arbitrary_types_allowed = True


class FlexibleModel(BaseModel):
    class Config(CommonConfig):
        arbitrary_types_allowed = True
        extra = Extra.allow


FlexModel = FlexibleModel


def base_conf():
    return CommonConfig


def main():
    pass


if __name__ == "__main__":
    main()
