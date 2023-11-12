try:
    from pydantic.v1 import (
        BaseModel,
        Extra,
        Field,
        PrivateAttr,
        StrictFloat,
        StrictInt,
        StrictStr,
        create_model,
        root_validator,
        validator,
    )
    from pydantic.v1.error_wrappers import ValidationError
    from pydantic.v1.fields import FieldInfo
    from pydantic.v1.generics import GenericModel
except ImportError:
    from pydantic import (
        BaseModel,
        Extra,
        Field,
        PrivateAttr,
        StrictFloat,
        StrictInt,
        StrictStr,
        create_model,
        root_validator,
        validator,
    )
    from pydantic.error_wrappers import ValidationError
    from pydantic.fields import FieldInfo
    from pydantic.generics import GenericModel

__all__ = [
    "BaseModel",
    "Field",
    "PrivateAttr",
    "root_validator",
    "validator",
    "create_model",
    "StrictFloat",
    "StrictInt",
    "StrictStr",
    "FieldInfo",
    "ValidationError",
    "Extra",
    "GenericModel",
]
