# clio

- 基于fastapi, sqlmode的框架

## RawContextMiddleware

- 请求上下文对象，可以像flask一样在任何地方获取当前请求的request对象

### 如何使用

- **添加RawContextMiddleware，需要添加到FastAPI拦截器的最后一个，FastAPI拦截器后添加的拦截器，最先执行**

```python
application = FastAPI()
application.add_middleware(SessionMiddleware, sqlalchemy=db)
application.add_middleware(RawContextMiddleware)
```

- 获取requestContext上下文

```
from clio.web import request_context

requext_context = request_context()
```

- 获取request

```python
from clio.web import request

current_request = request()
```

- 获取requestContext,可以在middleware中向requestContext中添加数据，在其它任何地方获取这个值，但要注意值添加的顺序，如果代码是在middleware之前执行，那么获取的值是空的

```python
from clio.web import request_context

current_request_context = request_context()
current_request_context.set("key", "value")
current_request_context.get("key")
current_request_context.remove("key")
```

## SessionMiddleware

- 支持全局获取db.session,session生命周期与request一致
- 支持同步与异步session

### 如何使用

- 初始化数据库

```python
import os
from clio import SQLAlchemy

database_uri = os.environ.get("DATABASE_URI")
db = SQLAlchemy(database_uri or "", echo=True)
```

- 添加SessionMiddleware

```python
application.add_middleware(SessionMiddleware, sqlalchemy=db)
```

- 任何地方获取session

```python
session = db.session
```

- 可以使用sqlachemy的query的方式操作数据库，也支持dbModel的select的方式操作

```python
# dbModel
heroes = db.session.exec(select(Hero).where(col(Hero.id) > 10)).all()

## sqlachemy的query
first = db.query(Hero).filter_by(id=1).first()
```

## SQLMODEL 数据库

### add

- session.add, session.commit后，**SQLAlchemy认为这个对象是过期的，如果直接打印整个对象会为空，需要手动refresh**

```python
hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

session = db.session
session.add(hero_1)
session.add(hero_2)
session.add(hero_3)
session.commit()

print(hero_1)  # {} 直接返回对象会为空

session.refresh(hero_2)
print(hero_2)  # secret_name='Pedro Parqueador' id=28 name='Spider-Boy' age=None
```

- **通过方法获取对象属性，会触发refresh**

```python
hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
session.add(hero_1)
session.commit()
print(hero_1.id)  # 1
```

### select

- select时语法不是keyword arguments，而是表达式,可以使用 ==, >=, <=, >, <,等

```python
heroes = db.session.exec(select(Hero).where(col(Hero.id) > 10)).all()
```

- 避免可空被lint报错，可以使用col函数

```python
heroes = db.session.exec(select(Hero).where(col(Hero.id) > 10)).all()
```

- 支持多个where条件，多个条件之间是and关系, 也可以使用and_函数
- 支持多个where条件，多个条件之间是or关系, 也可以使用or_函数

```python
# where可以传多个条件
heroes1 = db.session.exec(select(Hero).where(col(Hero.id) > 10, Hero.name == "Deadpond")).all()

# 或者用多个where
heroes2 = db.session.exec(select(Hero).where(col(Hero.id) > 10).where(Hero.name == "Deadpond")).all()

# and_
heroes3 = db.session.exec(select(Hero).where(and_(col(Hero.id) > 10, Hero.name == "Deadpond"))).all()

# or_
heroes4 = db.session.exec(select(Hero).where(or_(col(Hero.id) > 10, Hero.name == "Deadpond"))).all()
```

## alembic

### env.py新增sqlmodel的metadata
- import SQLModel
- import SqlModel的model
- target_metadata = SQLModel.metadata
- config.set_main_option("sqlalchemy.url", uri)

```python
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from sqlmodel import SQLModel  # NewAdded
from example.database.models import Hero  # NewAdded

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
uri = os.environ.get("DATABASE_URI")  # NewAdded
config.set_main_option("sqlalchemy.url", uri)  # NewAdded

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata  # NewAdded

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
```

### script.py.mako新增SqlModel的import

```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # NewAdded
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

```

### .env修改DATABASE_URI

### 创建创建迁移脚本,需要自己写逻辑

```python
alembic revision -m "create account table"
```

### 执行迁移
    - head 代表最新的版本
    - 可以加具体的版本号，如：alembic upgrade 1a2b3c4d5e6f
    - 从当前移动两个版本，可以提供十进制值“+N”或“-N”作为版本号，如：alembic upgrade +2
    - 降级，alembic downgrade -1

```python
alembic upgrade head
```

### 自动生成迁移脚本
- 需要指定target_metadata = SQLModel.metadata

```python
alembic revision --autogenerate -m "create account table"
```
