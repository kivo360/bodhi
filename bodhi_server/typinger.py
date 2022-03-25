from typing import Any, Dict, List, Union

DictStr = Dict[str, str]
DictStrAny = Dict[str, Any]
DictStrNested = Dict[str, Union[DictStrAny, DictStr, str]]
DictListStr = Dict[str, List[str]]
