from typing import Optional, Union

from loguru import logger

from pydantic import BaseModel
from pydantic.fields import Field, FieldInfo
from pydantic.main import ModelMetaclass
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, TypeVar, Union
from .utils import __dataclass_transform__

# _T = TypeVar("_T")


# def __dataclass_transform__(
#     *,
#     eq_default: bool = True,
#     order_default: bool = False,
#     kw_only_default: bool = False,
#     field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
# ) -> Callable[[_T], _T]:
#     return lambda a: a


@__dataclass_transform__(kw_only_default=True, field_descriptors=(Field, FieldInfo))
class ParameterMetaclass(ModelMetaclass):
    pass


class FlexibleModel(BaseModel):
    class Config:
        extra = "allow"
        arbitrary_types_allowed = "allow"


FlexModel = FlexibleModel


class Example(FlexModel):
    hello: str = "World"


def main():
    pass


if __name__ == "__main__":
    main()
