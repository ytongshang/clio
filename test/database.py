from enum import Enum
from typing import TypeAlias

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_serializer import SerializerMixin

from clio import sqlalchemy_table_to_pydantic

db = SQLAlchemy()


class User(db.Model, SerializerMixin):  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(64))


UserModel: TypeAlias = sqlalchemy_table_to_pydantic(User, "UserModel")  # type: ignore


# 会员类型
class MembershipType(Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


# payment_state 支付状态 1 已支付
class Members(db.Model, SerializerMixin):  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(
        String(15), unique=True, nullable=False, comment="手机号"
    )
    shop_name: Mapped[str] = mapped_column(
        String(15), unique=True, nullable=True, comment="店铺名称"
    )
    membership_type: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="会员类型 MembershipType"
    )
    card_key: Mapped[str] = mapped_column(
        String(18), nullable=True, unique=True, comment="秘钥"
    )
    mac_address: Mapped[str] = mapped_column(
        String(17), nullable=True, unique=True, comment="mac 地址"
    )
    amount: Mapped[float] = mapped_column(Float, nullable=True, comment="支付金额")
    payment_channel: Mapped[str] = mapped_column(
        String(10), nullable=True, comment="支付渠道"
    )
    order_number: Mapped[str] = mapped_column(String(30), nullable=True, comment="订单号")
    refund_state: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="退款状态 0：未退款 1：已退款 "
    )
    refund_amount: Mapped[float] = mapped_column(Float, nullable=True, comment="退款金额")
    refund_payment_channel: Mapped[str] = mapped_column(
        String(10), nullable=True, comment="退款支付渠道"
    )
    refund_order_number: Mapped[str] = mapped_column(
        String(30), nullable=True, unique=True, comment="退款单号"
    )
    active_date: Mapped[str] = mapped_column(String(30), nullable=True, comment="激活时间")
    expiration_date: Mapped[str] = mapped_column(
        String(30), nullable=True, comment="到期时间"
    )
    refund_date: Mapped[str] = mapped_column(String(30), nullable=True, comment="退款时间")
    create_date: Mapped[str] = mapped_column(String(30), nullable=True, comment="创建时间")


MembersModel: TypeAlias = sqlalchemy_table_to_pydantic(Members, "MembersModel")  # type: ignore


# 会员类型 爆款达人 同行达人 找达人 私信数 报名数 联系方式 店铺数
class ReportType(Enum):
    HOT = "hot"
    TRAVEL = "travel"
    FINDER = "finder"
    LETTER = "letter"
    APPLY = "apply"
    CONTACT = "apply"
    SHOP = "shop"


class ReportRecord(db.Model, SerializerMixin):  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, comment="会员ID")
    type: Mapped[str] = mapped_column(String(15), nullable=True, comment="数据类型")
    value: Mapped[str] = mapped_column(String(15), nullable=True, comment="值")
    uuid: Mapped[str] = mapped_column(String(15), nullable=False, comment="单次上传场景的唯一标识")


ReportRecordModel: TypeAlias = sqlalchemy_table_to_pydantic(ReportRecord, "ReportRecordModel")  # type: ignore


class DarenLoginInfo(db.Model, SerializerMixin):  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(10), nullable=True, comment="平台类型")
    url: Mapped[str] = mapped_column(String(30), nullable=True, comment="达人登录态缓存地址")
    avatar: Mapped[str] = mapped_column(String(30), nullable=True, comment="头像")
    author_id: Mapped[str] = mapped_column(
        String(30), nullable=True, comment="用户  authId"
    )
    outer_id: Mapped[str] = mapped_column(
        String(30), nullable=True, comment="用户outer_id"
    )
    count: Mapped[int] = mapped_column(
        Integer, default=0, primary_key=False, comment="使用计数"
    )
    state: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="登录态状态 0：无效 1：有效"
    )


DarenLoginInfoModel: TypeAlias = sqlalchemy_table_to_pydantic(  # type: ignore
    DarenLoginInfo, "DarenLoginInfoModel"  # type: ignore
)  # type: ignore


class DarenLoginInfoBindRecord(db.Model, SerializerMixin):  # type: ignore
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, unique=True, comment="会员ID")
    daren_login_state_record_id: Mapped[int] = mapped_column(
        Integer, comment="达人登录态记录ID"
    )


DarenLoginInfoBindRecordModel: TypeAlias = sqlalchemy_table_to_pydantic(  # type: ignore
    DarenLoginInfoBindRecord, "DarenLoginInfoBindRecordModel"  # type: ignore
)  # type: ignore


def database_config():
    return {
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://drill_root:nkOq7anGmV@112.124.14.28:3306/drill",
        "SQLALCHEMY_POOL_SIZE": 10,
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_recycle": 120},
        "SQLALCHEMY_ECHO": True,
    }


def init_database(app):
    config = database_config()
    app.config.from_mapping(config)
    db.init_app(app)
    return db


async def create_table(app):
    async with app.app_context():
        # db.drop_all()
        db.create_all()
    return db
