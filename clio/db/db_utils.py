from typing import Optional, Type

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def sqlalchemy_table_to_pydantic(table, name: str) -> Type[BaseModel]:
    # 从 SQLAlchemy 表中提取列信息
    columns = table.__table__.columns
    fields = {}
    for column in columns:
        field_name = column.name
        nullable = column.nullable
        field_type = column.type.python_type
        field_info = FieldInfo(description=column.comment, default_value=column.default)
        if nullable:
            fields[field_name] = (Optional[field_type], field_info)
        else:
            fields[field_name] = (field_type, field_info)
    return create_model(name, **fields)
