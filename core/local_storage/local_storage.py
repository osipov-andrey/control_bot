import asyncio
from functools import wraps

from pathlib import Path
from sqlite3 import Connection, IntegrityError
from typing import List, Optional

import aiosqlite
from sqlalchemy import null
from sqlalchemy.orm import Query

from core.local_storage import queryes
from core.local_storage.db_enums import UserEvents
from core.local_storage.exceptions import AlreadyHasItException, NoSuchUser
from core.local_storage.schema import *


def connect_to_db(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            if kwargs.get("connection"):
                return await method(self, *args, **kwargs)
            async with aiosqlite.connect(LocalStorage.db) as db:
                return await method(self, *args, connection=db, **kwargs)
        except IntegrityError as err:
            # Запись нарушает ограничение уникальности
            if err.args[0].startswith("UNIQUE constraint failed"):
                raise AlreadyHasItException
            else:
                raise
    return wrapper


class LocalStorage:
    db = Path(__file__).parent.absolute().joinpath("control_bot.db")

    @connect_to_db
    async def upsert_user(
            self,
            tg_id: int,
            tg_username: str,
            name: Optional[str] = null(),
            phone: Optional[str] = null(),
            is_admin: Optional[bool] = False,
            *,
            connection
    ):

        user_exists = await self.get_user(tg_id, connection=connection)
        if user_exists:
            query = queryes.update_user(
                tg_id, tg_username, name, phone, is_admin
            )
            result = UserEvents.UPDATED
        else:
            query = queryes.insert_user(
                tg_id, tg_username, name, phone, is_admin
            )
            result = UserEvents.CREATED
        await connection.execute(self._get_sql(query))
        await connection.commit()
        return result

    # @connect_to_db
    # async def check_user_exists(self, user_telegram_id: int, *, connection):
    #     user = await self.get_user(user_telegram_id, connection=connection)
    #     if not user:
    #         raise NoSuchUser

    @connect_to_db
    async def get_user(self, tg_id: int, *, connection) -> User:

        user_query = users_table.select().where(
            users_table.c.telegram_id == tg_id
        )
        user = await connection.execute(self._get_sql(user_query))
        user = await user.fetchone()
        if not user:
            raise NoSuchUser
        user = User(*user)
        return user

    @connect_to_db
    async def get_all_users(self, *, connection):
        # TODO: generator
        users_query = users_table.select()
        users = await connection.execute(self._get_sql(users_query))
        users = await users.fetchall()
        users = [User(*user) for user in users]
        return users

    @connect_to_db
    async def get_admins(self, *, connection) -> List[User]:
        admins_query = users_table.select().where(
            users_table.c.is_admin == 1
        )
        admins = await connection.execute(self._get_sql(admins_query))
        admins = await admins.fetchall()
        admins = [User(*admin) for admin in admins]
        return admins

    @connect_to_db
    async def save_channel(self, name: str, *, connection):
        query: Query = channel_table.insert().values({
            'name': name
        })
        await connection.execute(self._get_sql(query))
        await connection.commit()

    @connect_to_db
    async def get_subscribers(self, channel: str, *, connection) -> List[User]:
        subscribers_query = queryes.get_subscribers(channel)
        subscribers = await connection.execute(self._get_sql(subscribers_query))
        subscribers = await subscribers.fetchall()
        subscribers = [User(*subs) for subs in subscribers]
        return subscribers

    @connect_to_db
    async def channel_subscribe(self, user_telegram_id: int, channel: str, *, connection) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id, connection=connection)
        # TODO: использовать этого пользователя в дальнейшем запросе
        subscribe_query = channels_users_associations.insert().values({
            "user_id": queryes.get_user_id_query(user_telegram_id),
            "channel_id": queryes.get_channel_id_query(channel)
        })
        result = await connection.execute(self._get_sql(subscribe_query))
        await connection.commit()
        return bool(result.rowcount)

    @connect_to_db
    async def channel_unsubscribe(self, user_telegram_id: int, channel: str, *, connection) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id, connection=connection)
        # TODO: использовать этого пользователя в дальнейшем запросе
        unsubscribe_query = queryes.get_unsubscribe_query(user_telegram_id, channel)
        result = await connection.execute(self._get_sql(unsubscribe_query))
        await connection.commit()
        return bool(result.rowcount)

    @connect_to_db
    async def grant(self, user_telegram_id: int, actuator_name: str, *, connection) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id, connection=connection)
        # TODO: использовать этого пользователя в дальнейшем запросе
        grant_query = queryes.grant_query(user_telegram_id, actuator_name)
        result = await connection.execute(self._get_sql(grant_query))
        await connection.commit()
        return bool(result.rowcount)

    @connect_to_db
    async def revoke(self, user_telegram_id: int, actuator_name: str, *, connection) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id, connection=connection)
        # TODO: использовать этого пользователя в дальнейшем запросе
        revoke_query = queryes.revoke_query(user_telegram_id, actuator_name)
        result = await connection.execute(self._get_sql(revoke_query))
        await connection.commit()
        return bool(result.rowcount)

    @connect_to_db
    async def create_actuator(self, name: str, description: Optional[str] = None, *, connection):
        result = await connection.execute(
            self._get_sql(queryes.create_actuator_query(name, description))
        )
        await connection.commit()
        return result

    @connect_to_db
    async def delete_actuator(self, name: str, *, connection):
        result = await connection.execute(self._get_sql(queryes.delete_actuator_query(name)))
        await connection.commit()
        return result

    @connect_to_db
    async def user_has_grant(self, user_telegram_id: int, actuator_name: str, *, connection) -> bool:
        result = await connection.execute(
            self._get_sql(queryes.get_has_grant_query(
                user_telegram_id, actuator_name
            ))
        )
        result = await result.fetchone()
        return bool(result)

    @connect_to_db
    async def get_granters(self, actuator_name: str, *, connection) -> List[User]:
        result = await connection.execute(
            self._get_sql(queryes.get_granters_query(actuator_name))
        )
        result = await result.fetchall()
        granters = [User(*user) for user in result]
        return granters

    @connect_to_db
    async def get_actuators(self, *, connection) -> List[Actuator]:
        result = await connection.execute(
            self._get_sql(queryes.get_all_actuators())
        )
        actuators = [Actuator(*actuator) for actuator in await result.fetchall()]
        return actuators

    @staticmethod
    def _get_sql(query: Query):
        return str(query.compile(compile_kwargs={"literal_binds": True}))


# if __name__ == '__main__':
    # from sqlalchemy import create_engine
    # from sqlalchemy.engine import reflection
    #
    #
    # engine = create_engine('sqlite:///control_bot.db')
    # insp = reflection.Inspector.from_engine(engine)
    # print(insp.get_columns(users_table))

    # store = LocalStorage()
    # user = asyncio.run(store.get_user(172698654))
    # admins = asyncio.run(store.get_admins())
    # print(user)
    # print(admins)
    # asyncio.run(store.save_channel('123'))

# id
# name
# phone
# username
# telegram_id