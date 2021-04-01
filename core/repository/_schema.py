from collections import namedtuple
from typing import Type

from sqlalchemy import Table, Column, MetaData, Boolean, Integer, String
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, UniqueConstraint


def _create_mapping(table: Table) -> Type[tuple]:
    fields = table.c.keys()
    name: str = _to_pascal_case(table.name)
    mapping = namedtuple(name, fields)
    return mapping


def _to_pascal_case(snake_case: str) -> str:
    parts = snake_case.split("_")
    pascal = "".join(part.capitalize() for part in parts)
    return pascal


metadata = MetaData()


channels_users_associations = Table(
    "user_channel",
    metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "channel_id",
        ForeignKey("channel.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    PrimaryKeyConstraint("user_id", "channel_id", name="user_channel_pk"),
)
UserChannel = _create_mapping(channels_users_associations)


actuators_users_associations = Table(
    "user_actuator",
    metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "actuator_id",
        Integer,
        ForeignKey("actuator.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    PrimaryKeyConstraint("user_id", "actuator_id", name="user_actuator_pk"),
)
UserActuator = _create_mapping(actuators_users_associations)

users_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("telegram_id", Integer, unique=True, index=True, nullable=False),
    Column("telegram_username", String, unique=True, nullable=False),
    Column("name", String, nullable=True),
    Column("phone_number", String, nullable=True),
    Column("is_admin", Boolean, default=False),
    UniqueConstraint("telegram_id", "telegram_username", name="uq_id_user"),
)
User = _create_mapping(users_table)


channel_table = Table(
    "channel",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, unique=True, nullable=False, index=True),
    Column("description", String, nullable=True),
)
Channel = _create_mapping(channel_table)


actuators_table = Table(
    "actuator",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, unique=True, nullable=False, index=True),
    Column("description", String, nullable=True),
)
Actuator = _create_mapping(actuators_table)
