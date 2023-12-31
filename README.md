# clio

## 数据库

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

