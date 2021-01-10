import asyncio
from functools import wraps
from pathlib import Path
from typing import Optional

import aiosqlite
from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table, \
    ForeignKeyConstraint, UniqueConstraint, insert, null
from sqlalchemy.orm import Query, backref, relationship

from core.local_storage.db_enums import UserEvents

metadata = MetaData()


channels_users_associations = Table(
    "user_channel",
    metadata,
    Column("user_id", Integer, ForeignKey('user.id')),
    Column("channel_id", ForeignKey('channel.id')),
)


actuators_users_associations = Table(
    "user_actuator",
    metadata,
    Column("user_id", Integer, ForeignKey('user.id')),
    Column("actuator_id", ForeignKey('actuator.id')),
)


users_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("telegram_id", Integer, unique=True, index=True, nullable=False),
    Column("telegram_username", String, unique=True, nullable=False),
    Column("name", String, nullable=True),
    Column("phone_number", String, nullable=True),
    Column("is_admin", Boolean, default=False),
    UniqueConstraint("telegram_id", "telegram_username", name="uq_id_user")
)


channel_table = Table(
    "channel",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, unique=True, nullable=False, index=True),
)


actuators_table = Table(
    "actuator",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, unique=True, nullable=False, index=True),
    Column("description", String, nullable=True),
)


def auto_connection(method):
    # TODO: хрень какая-то
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        if kwargs.get("connection") is None:
            kwargs["connection"] = aiosqlite.connect(self.db)
        return await method(self, *args, **kwargs)

    return wrapper


class LocalStorage:

    def __init__(self):
        self.db = Path(__file__).parent.absolute().joinpath("control_bot.db")

    def connection(self):
        return aiosqlite.connect(self.db)

    @auto_connection
    async def upsert_user(
            self,
            tg_id: int,
            tg_username: str,
            name: Optional[str] = null(),
            phone: Optional[str] = null(),
            is_admin: Optional[bool] = False,
            *,
            connection: aiosqlite.Connection
    ):

        async with connection as db:

            insert_query = users_table.insert().values(
                {
                    "telegram_id": tg_id,
                    "telegram_username": tg_username,
                    "name": name,
                    "phone_number": phone,
                    "is_admin": is_admin
                }
            )

            update_query = users_table.update().values({
                "name": name,
                "phone_number": phone,
                "is_admin": is_admin
            }).where(
                users_table.c.telegram_id == tg_id
                or users_table.c.telegram_username == tg_username
            )

            user_exists = await self.get_user(tg_id)
            if user_exists:
                query = update_query
                result = UserEvents.UPDATED
            else:
                query = insert_query
                result = UserEvents.CREATED
            await db.execute(self._get_sql(query))
            await db.commit()
            return result

    @auto_connection
    async def get_user(
        self,
        tg_id: int,
        *,
        connection: aiosqlite.Connection
    ):
        async with connection as db:
            user_query = users_table.select().where(
                users_table.c.telegram_id == tg_id
            )
            user = await db.execute(self._get_sql(user_query))
            user = await user.fetchone()
            return user

    @auto_connection
    async def get_all_users(self, *, connection: aiosqlite.Connection):
        # TODO: generator
        async with connection as db:
            users_query = users_table.select()
            users = await db.execute(self._get_sql(users_query))
            users = await users.fetchall()
            return users

    @auto_connection
    async def get_admins(self, *, connection: aiosqlite.Connection):
        async with connection as db:
            admins_query = users_table.select().where(
                users_table.c.is_admin == 1
            )
            admins = await db.execute(self._get_sql(admins_query))
            admins = await admins.fetchall()
            return admins

    @auto_connection
    async def save_channel(
            self,
            name: str,
            *,
            connection: aiosqlite.Connection
    ):
        async with aiosqlite.connect(self.db) as db:
            query: Query = channel_table.insert().values({
                'name': name
            })

            await db.execute(self._get_sql(query))
            await db.commit()

    async def subscribe_user_on_channel(self):
        ...

    async def unsubscribe_user_on_channel(self):
        ...

    async def grant_client_to_the_user(self):
        ...

    async def revoke_client_from_the_user(self):
        ...

    @staticmethod
    def _get_sql(query: Query):
        return str(query.compile(compile_kwargs={"literal_binds": True}))


if __name__ == '__main__':
    # from sqlalchemy import create_engine
    # from sqlalchemy.engine import reflection
    #
    #
    # engine = create_engine('sqlite:///control_bot.db')
    # insp = reflection.Inspector.from_engine(engine)
    # print(insp.get_columns(users_table))

    store = LocalStorage()
    asyncio.run(store.save_user(6, "6", is_admin=False))
    # asyncio.run(store.save_channel('123'))

# id
# name
# phone
# username
# telegram_id