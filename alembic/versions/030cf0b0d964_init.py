"""init

Revision ID: 030cf0b0d964
Revises: 
Create Date: 2024-01-14 17:23:11.406729

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "030cf0b0d964"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hero",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("secret_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("migrations")
    op.drop_table("users")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("username", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("password", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("nickname", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("avatar", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "role",
            postgresql.ENUM("USER", "ADMIN", name="users_role_enum"),
            server_default=sa.text("'USER'::users_role_enum"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "disabled",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="PK_a3ffb1c0c8416b9fc6f907b7433"),
        sa.UniqueConstraint("email", name="UQ_97672ac88f789774dd47f7c8be3"),
    )
    op.create_table(
        "migrations",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="PK_8c82d7f526340ab734260ea46be"),
    )
    op.drop_table("hero")
    # ### end Alembic commands ###