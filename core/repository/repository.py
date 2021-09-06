from contextlib import contextmanager, asynccontextmanager
from pathlib import Path
from sqlite3 import Cursor, IntegrityError
from typing import List, Optional, Union, Iterable, Any
from functools import wraps

import aiosqlite
from sqlalchemy import null, text
from sqlalchemy.engine import Result, ScalarResult
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from core.exceptions import AlreadyHasItException, NoSuchUser, NoSuchChannel
from . import _queryes
from .db_enums import UserEvents
from ._schema import *


PATH_TO_DB = Path(__file__).parent.absolute().joinpath("db_dump").joinpath("control_bot.sqlite")


def first(sequence: Iterable) -> Optional[Any]:
    return next(iter(sequence), None)


@asynccontextmanager
async def db_session(path_to_db: Path = PATH_TO_DB) -> AsyncSession:
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{str(path_to_db)}",
        echo=True,
    )

    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                yield session
            except IntegrityError as err:
                # Запись нарушает ограничение уникальности
                if err.args[0].startswith("UNIQUE constraint failed"):
                    raise AlreadyHasItException
                else:
                    raise
            finally:
                engine.dispose()


# def connect_to_db(method):
#     @wraps(method)
#     async def wrapper(self, *args, **kwargs):
#         try:
#             if kwargs.get("connection"):
#                 return await method(self, *args, **kwargs)
#             async with aiosqlite.connect(Repository.db) as db:
#                 return await method(self, *args, connection=db, **kwargs)
#         except IntegrityError as err:
#             # Запись нарушает ограничение уникальности
#             if err.args[0].startswith("UNIQUE constraint failed"):
#                 raise AlreadyHasItException
#             else:
#                 raise
#
#     return wrapper


class Repository:
    def __init__(self, path_to_db: Path = PATH_TO_DB):
        self.db = path_to_db

    async def upsert_user(
        self,
        tg_id: int,
        tg_username: str,
        name: Optional[str] = null(),
        phone: Optional[str] = null(),
        is_admin: Optional[bool] = False,
    ):
        async with db_session(self.db) as session:  # type: AsyncSession
            # TODO: get_user()
            user_exists: Result = await session.execute(
                select(User).where(User.telegram_id == tg_id)
            )
            if not user_exists.scalar():
                # TODO: insert_user()
                session.add(
                    User(
                        telegram_id=tg_id,
                        telegram_username=tg_username,
                        name=name,
                        phone_number=phone,
                        is_admin=is_admin,
                    )
                )
                result = UserEvents.CREATED
            else:
                # TODO: update_user()
                await session.execute(
                    text(
                        self._get_sql(
                            _queryes.update_user(tg_id, tg_username, name, phone, is_admin)
                        )
                    )
                )
                result = UserEvents.UPDATED
            await session.commit()
            return result

    async def get_user(self, tg_id: int) -> User:
        user_query = select(User).where(User.telegram_id == tg_id)
        result: ScalarResult = await self._execute_simple_query(user_query)
        user: Optional[User] = first(result)
        if not user:
            raise NoSuchUser
        return user

    async def get_all_users(self) -> List[User]:
        # TODO: generator
        users_query = users_table.select()
        users = await self._execute_simple_query(users_query)
        users = [User(*user) for user in users]
        return users

    async def get_admins(self) -> List[User]:
        admins_query = users_table.select().where(users_table.c.is_admin == 1)
        admins = await self._execute_simple_query(admins_query)
        admins = [User(*admin) for admin in admins]
        return admins

    async def get_channel(self, channel_name: str) -> Channel:
        user_query = channel_table.select().where(channel_table.c.name == channel_name)
        channel = await self._execute_simple_query(user_query, fetchall=False)
        if not channel:
            raise NoSuchChannel
        channel = Channel(*channel)
        return channel

    async def all_channels(self) -> List[Channel]:
        query: Query = channel_table.select()
        result = await self._execute_simple_query(query, fetchall=True)
        return [Channel(*channel) for channel in result]

    async def save_channel(self, name: str, description: str) -> bool:
        query: Query = channel_table.insert().values({"name": name, "description": description})
        result = await self._execute_simple_query(query, commit=True)
        return result.rowcount == 1

    async def delete_channel(self, name: str) -> bool:
        query: Query = channel_table.delete().where(channel_table.c.name == name)
        result = await self._execute_simple_query(query, commit=True)
        return result.rowcount == 1

    async def get_subscribers(self, channel: str) -> List[User]:
        subscribers_query = _queryes.get_subscribers(channel)
        subscribers = await self._execute_simple_query(subscribers_query)
        subscribers = [User(*subs) for subs in subscribers]
        return subscribers

    async def channel_subscribe(self, user_telegram_id: int, channel: str) -> bool:
        user = await self.get_user(user_telegram_id)
        channel = await self.get_channel(channel)
        subscribe_query = channels_users_associations.insert().values(
            {"user_id": user.id, "channel_id": channel.id}
        )
        result = await self._execute_simple_query(subscribe_query, commit=True)
        return bool(result.rowcount)

    async def channel_unsubscribe(self, user_telegram_id: int, channel: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        unsubscribe_query = _queryes.get_unsubscribe_query(user_telegram_id, channel)
        result = await self._execute_simple_query(unsubscribe_query, commit=True)
        return bool(result.rowcount)

    async def grant(self, user_telegram_id: int, actuator_name: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        grant_query = _queryes.grant_query(user_telegram_id, actuator_name)
        result = await self._execute_simple_query(grant_query, commit=True)
        return bool(result.rowcount)

    async def revoke(self, user_telegram_id: int, actuator_name: str) -> bool:
        # Проверим есть ли вообще такой юзер
        await self.get_user(user_telegram_id)
        # TODO: использовать этого пользователя в дальнейшем запросе
        revoke_query = _queryes.revoke_query(user_telegram_id, actuator_name)
        result = await self._execute_simple_query(revoke_query, commit=True)
        return bool(result.rowcount)

    async def create_actuator(self, name: str, description: Optional[str] = None):
        result = await self._execute_simple_query(
            _queryes.create_actuator_query(name, description), commit=True
        )
        return result

    async def delete_actuator(self, name: str):
        result = await self._execute_simple_query(_queryes.delete_actuator_query(name), commit=True)
        return result

    async def user_has_grant(self, user_telegram_id: int, actuator_name: str) -> bool:
        result = await self._execute_simple_query(
            _queryes.get_has_grant_query(user_telegram_id, actuator_name),
            fetchall=False,
        )
        return bool(result)

    async def get_granters(self, actuator_name: str) -> List[User]:
        granters = await self._execute_simple_query(_queryes.get_granters_query(actuator_name))
        granters = [User(*user) for user in granters]
        return granters

    async def get_actuators(self) -> List[Actuator]:
        actuators = await self._execute_simple_query(_queryes.get_all_actuators())
        actuators: list = [Actuator(*actuator) for actuator in actuators]
        return actuators

    async def get_user_subscribes(self, user_telegram_id: int) -> List[Channel]:
        channels = await self._execute_simple_query(
            _queryes.get_user_subscribes_query(user_telegram_id)
        )
        channels: list = [Channel(*channel) for channel in channels]
        return channels

    async def _execute_simple_query(self, query: Query) -> ScalarResult:
        with db_session() as session:  # type: AsyncSession
            result: Result = await session.execute(query)
            return result.scalars()

    @staticmethod
    def _get_sql(query: Query):
        query = str(query.compile(compile_kwargs={"literal_binds": True}))
        return query
