import json
from json import JSONEncoder
from typing import Any, Callable, Dict, Optional, Set, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

IncEx = Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any]]


def object_to_json(
    obj: Any,
    include: Optional[IncEx] = None,
    exclude: Optional[IncEx] = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: Optional[Dict[Any, Callable[[Any], Any]]] = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    """
    obj: The input object to convert to JSON.
    include: Pydantic's `include` parameter, passed to Pydantic models to set the
        fields to include.
    exclude: Pydantic's `exclude` parameter, passed to Pydantic models to set the
        fields to exclude.
    by_alias: Pydantic's `by_alias` parameter, passed to Pydantic models to define if
        the output should use the alias names (when provided) or the Python
        attribute names. In an API, if you set an alias, it's probably because you
        want to use it in the result, so you probably want to leave this set to
        `True`.
    exclude_unset: Pydantic's `exclude_unset` parameter, passed to Pydantic models to define
        if it should exclude from the output the fields that were not explicitly
        set (and that only had their default values).
    exclude_defaults: Pydantic's `exclude_defaults` parameter, passed to Pydantic models to define
        if it should exclude from the output the fields that had the same default
        value, even when they were explicitly set.
    exclude_none: Pydantic's `exclude_none` parameter, passed to Pydantic models to define
        if it should exclude from the output any fields that have a `None` value.
    custom_encoder: Pydantic's `custom_encoder` parameter, passed to Pydantic models to define
        a custom encoder.
    sqlalchemy_safe: Exclude from the output any fields that start with the name `_sa`.
        This is mainly a hack for compatibility with SQLAlchemy objects, they
        store internal SQLAlchemy-specific state in attributes named with `_sa`,
        and those objects can't (and shouldn't be) serialized to JSON.
    """
    if obj is None:
        return None
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "to_json"):
        return obj.to_json()
    return jsonable_encoder(
        obj,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )


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
