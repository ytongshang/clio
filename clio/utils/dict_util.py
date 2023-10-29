from enum import Enum
from typing import Mapping, Sequence

from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1


def object_to_dict(obj):
    if obj is None:
        return None
    if isinstance(obj, (int, float, str, bool)):
        return obj
    if isinstance(obj, Mapping):
        result = {}
        for key, value in obj.items():
            result[key] = object_to_dict(value)
        return result
    if isinstance(obj, Sequence):
        result = []
        for item in obj:
            result.append(object_to_dict(item))
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
    raise Exception(f"unsupported type: {type(obj)}")
