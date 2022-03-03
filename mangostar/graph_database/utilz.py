import uuid
from hashlib import sha256
from typing import Tuple

import orjson
from auto_all import end_all
from auto_all import start_all
from decorator import decorate
from frozendict import frozendict
from genson import SchemaBuilder
from pyrsistent import freeze
from pyrsistent import pmap
from pyrsistent import thaw
from stringcase import snakecase

start_all(globals())


def _memoize(func, *args, **kw):
    if kw:              # frozenset is used to ensure hashability
        key = freeze(args), freeze(kw)
    else:
        key = freeze(args)
    cache = func.cache  # attribute added by memoize
    if key not in cache:
        cache[key] = func(*args, **kw)
    return cache[key]


def memoize(f):
    """
    A simple memoize implementation. It works by adding a .cache dictionary
    to the decorated function. The cache will grow indefinitely, so it is
    your responsibility to clear it, if needed.
    """
    f.cache = {}
    return decorate(f, _memoize)


js_keys = ['$schema', 'type', 'properties']


def is_json_schema(item: dict) -> Tuple[bool, bool]:
    """Determines if the input is a json schema. If it is empty we also 
    return a second boolean wether it'll be a good idea to continue logic forward.

    Args:
        item (dict): The dict to check.

    Returns:
        Tuple[bool, bool]: True if dict is a json schema, second boolean says to continue value.
    """
    if not item:
        return False, False
    top_level_keys = item.keys()

    is_schema = all((key in top_level_keys) for key in js_keys)
    return is_schema, True


def gen_hex_id():
    return uuid.uuid4().hex


@memoize
def json_hash(item: dict):
    return sha256(
        orjson.dumps(
            item, option = orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS
        )
    ).hexdigest()


def to_snake(name: str) -> str:
    return snakecase(name)


@memoize
def dict_to_schema(item: dict, check = False) -> dict:
    if check:
        is_scheme, is_cont = is_json_schema(item)
        if is_scheme or not is_cont:
            return item

    scheme_build = SchemaBuilder()
    scheme_build.add_object(item)
    return scheme_build.to_schema()


@memoize
def schema_hash(item: dict):
    return json_hash(dict_to_schema(item, check = True))


def combine_schemas(item_one: dict, item_two: dict) -> dict:
    _potetial_one = item_one
    is_one, is_cont_one = is_json_schema(item_one)

    if not is_one:
        if is_cont_one:
            _potetial_one = dict_to_schema(item_one)
        else:
            return dict_to_schema(item_two)

    _potetial_two = item_two
    is_two, is_cont_two = is_json_schema(item_two)

    if not is_two:
        if is_cont_two:
            _potetial_two = dict_to_schema(item_two)
        else:
            return _potetial_one

    merge_builder = SchemaBuilder()
    merge_builder.add_schema(_potetial_one)
    merge_builder.add_schema(_potetial_two)
    return merge_builder.to_schema()


end_all(globals())
