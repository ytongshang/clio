import json
from enum import Enum
from json import JSONEncoder
from typing import Mapping, Sequence

from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1


def object_to_json(obj):
    if obj is None:
        return None
    if isinstance(obj, (int, float, str, bool)):
        return obj
    if isinstance(obj, Mapping):
        result = {}
        for key, value in obj.items():
            result[key] = object_to_json(value)
        return result
    if isinstance(obj, Sequence):
        result = []
        for item in obj:
            result.append(object_to_json(item))
        return result
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, BaseModelV1):
        return obj.dict()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "to_json"):
        return obj.to_json()
    raise Exception(f"object_to_json unsupported type: {type(obj)}")


def hack_json():
    # type: ignore
    def _default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, BaseModelV1):
            return obj.dict()
        return object_to_json(obj)

    _default.default = JSONEncoder.default  # type: ignore
    JSONEncoder.default = _default  # type: ignore


def pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def short_json(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
