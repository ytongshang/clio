from typing import List

from fastapi import APIRouter
from sqlmodel import and_, col, or_, select

from clio import HttpResponse
from clio.utils.log import Log
from example.database.database import db
from example.database.models import Hero
from example.model.test import TestBody, TestResp

test_api_router = APIRouter(prefix="/test")


@test_api_router.post("/test")
async def test(test_body: TestBody):
    await test()
    Log.info(f"test_body: {test_body}")
    resp = TestResp(e="e")
    return HttpResponse.success(resp)


@test_api_router.get("/db/add")
async def test_db_add() -> HttpResponse[List[Hero]]:
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    session = db.session
    session.add(hero_1)
    session.add(hero_2)
    session.add(hero_3)
    session.commit()
    # 如果直接返回对象必须要refresh
    session.refresh(hero_1)
    session.refresh(hero_2)
    # session.refresh(hero_3)
    print(hero_2)
    print(hero_3)
    return HttpResponse.success([hero_1, hero_2, hero_3])


@test_api_router.get("/db/add2")
async def test_db_add2() -> HttpResponse[int]:
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")

    session = db.session
    session.add(hero_1)
    session.commit()
    return HttpResponse.success(hero_1.id)


@test_api_router.get("/db/get")
async def test_db_get() -> HttpResponse[List[Hero]]:
    heroes = db.session.exec(select(Hero)).all()
    return HttpResponse.success(heroes)


@test_api_router.get("/db/filter")
async def test_filter_filter() -> HttpResponse[List[Hero]]:
    # Hero.id是可空类型，代码lint会报错，可以用col这个方式绕过
    heroes = db.session.exec(select(Hero).where(col(Hero.id) > 10)).all()
    return HttpResponse.success(heroes)


@test_api_router.get("/db/filter2")
async def test_filter_filter2() -> HttpResponse[List[Hero]]:
    # where可以传多个条件
    heroes1 = db.session.exec(
        select(Hero).where(col(Hero.id) > 10, Hero.name == "Deadpond")
    ).all()
    # 或者用多个where
    heroes2 = db.session.exec(
        select(Hero).where(col(Hero.id) > 10).where(Hero.name == "Deadpond")
    ).all()
    # 或者用and_
    heroes3 = db.session.exec(
        select(Hero).where(and_(col(Hero.id) > 10, Hero.name == "Deadpond"))
    ).all()
    # 用or_
    heroes4 = db.session.exec(
        select(Hero).where(or_(col(Hero.id) > 10, Hero.name == "Deadpond"))
    ).all()
    return HttpResponse.success(heroes1 + heroes2 + heroes3)


@test_api_router.get("/db/query")
async def test_query() -> HttpResponse[List[Hero]]:
    heroes1 = db.query(Hero).filter(Hero.id > 10).all()
    print(heroes1)
    return HttpResponse.success(heroes1)


@test_api_router.get("/db/update")
async def test_update() -> HttpResponse[List[Hero]]:
    first = db.query(Hero).filter_by(id=1).first()
    resp = []
    if first:
        first.name = "test"
        db.session.commit()
        db.session.refresh(first)
        resp.append(first)
    return HttpResponse.success(resp)
