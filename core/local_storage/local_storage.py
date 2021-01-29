import asyncio
from functools import wraps

from pathlib import Path
from sqlite3 import Connection, Cursor, IntegrityError
from typing import List, Optional, Union

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

    async def upsert_user(
            self,
            tg_id: int,
            tg_username: str,
            name: Optional[str] = null(),
            phone: Optional[str] = null(),
            is_admin: Optional[bool] = False,
    ):
        try:
            user_exists = await self.get_user(tg_id)
            query = queryes.update_user(
                tg_id, tg_username, name, phone, is_admin
            )
            result = UserEvents.UPDATED
        except NoSuchUser:
            query = queryes.insert_user(
                tg_id, tg_username, name, phone, is_admin
            )
            result = UserEvents.CREATED

        await self._execute_query(query, commit=True)
        return result

    # @connect_to_db
    # async def check_user_exists(self, user_telegram_id: int, *, connection):
    #     user = await self.get_user(user_telegram_id, connection=connection)
    #     if not user:
    #         raise NoSuchUser

    async def get_user(self, tg_id: int) -> User:
        user_query = users_table.select().where(
            users_table.c.telegram_id == tg_id
        )
        user = await self._execute_query(user_query, fetchall=False)
        if not user:
            raise NoSuchUser
        user = User(*user)
        return user

    async def get_all_users(self):
        # TODO: generator
        users_query = users_table.select()
        users = await self._execute_query(users_query)
        users = [User(*user) for user in users]
        return users

    async def get_admins(self) -> List[User]:
        admins_query = users_table.select().where(
            users_table.c.is_admin == 1
        )
        admins = await self._execute_query(admins_query)
        admins = [User(*admin) for admin in admins]
        return admins

    async def save_channel(self, name: str):
        query: Query = channel_table.insert().values({'name': name})
        await self._execute_query(query, commit=True)

    async def get_subscribers(self, channel: str) -> List[User]:
        subscribers_query = queryes.get_subscribers(channel)
        subscribers = await self._execute_query(subscribers_query)
        subscribers = [User(*subs) for subs in subscribers]
        return subscribers

    async def channel_subscribe(self, user_telegram_id: int, channel: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        subscribe_query = channels_users_associations.insert().values({
            "user_id": queryes.get_user_id_query(user_telegram_id),
            "channel_id": queryes.get_channel_id_query(channel)
        })
        result = await self._execute_query(subscribe_query, commit=True)
        return bool(result.rowcount)

    async def channel_unsubscribe(self, user_telegram_id: int, channel: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        unsubscribe_query = queryes.get_unsubscribe_query(user_telegram_id, channel)
        result = await self._execute_query(unsubscribe_query, commit=True)
        return bool(result.rowcount)

    async def grant(self, user_telegram_id: int, actuator_name: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        grant_query = queryes.grant_query(user_telegram_id, actuator_name)
        result = await self._execute_query(grant_query, commit=True)
        return bool(result.rowcount)

    async def revoke(self, user_telegram_id: int, actuator_name: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        revoke_query = queryes.revoke_query(user_telegram_id, actuator_name)
        result = await self._execute_query(revoke_query, commit=True)
        return bool(result.rowcount)

    async def create_actuator(self, name: str, description: Optional[str] = None):
        result = await self._execute_query(
            queryes.create_actuator_query(name, description), commit=True
        )
        return result

    async def delete_actuator(self, name: str):
        result = await self._execute_query(
            queryes.delete_actuator_query(name), commit=True
        )
        return result

    async def user_has_grant(self, user_telegram_id: int, actuator_name: str) -> bool:
        result = await self._execute_query(
            queryes.get_has_grant_query(user_telegram_id, actuator_name), fetchall=False
        )
        return bool(result)

    async def get_granters(self, actuator_name: str) -> List[User]:
        granters = await self._execute_query(queryes.get_granters_query(actuator_name))
        granters = [User(*user) for user in granters]
        return granters

    async def get_actuators(self) -> List[Actuator]:
        actuators = await self._execute_query(queryes.get_all_actuators())
        actuators = [Actuator(*actuator) for actuator in actuators]
        return actuators

    async def get_user_subscribes(self, user_telegram_id: int) -> List[Channel]:
        channels = await self._execute_query(queryes.get_user_subscribes_query(user_telegram_id))
        channels = [Channel(**channel) for channel in channels]
        return channels

    @connect_to_db
    async def _execute_query(
            self, query: Query, *, connection, fetchall=True, commit=False
    ) -> Union[tuple, List[tuple], Cursor]:
        cursor = await connection.execute(self._get_sql(query))
        if commit:
            await connection.commit()
            return cursor
        if fetchall is True:
            result = await cursor.fetchall()
        else:
            result = await cursor.fetchone()
        return result

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