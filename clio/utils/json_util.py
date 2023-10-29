import json
from json import JSONEncoder

from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1


def hack_json():
    # type: ignore
    def _default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, BaseModelV1):
            return obj.dict()
        return getattr(obj.__class__, "to_json")(obj)

    _default.default = JSONEncoder.default  # type: ignore
    JSONEncoder.default = _default  # type: ignore


def pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def short_json(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
