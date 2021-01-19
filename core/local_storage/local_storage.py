import asyncio

from pathlib import Path
from typing import List, Optional

import aiosqlite
from sqlalchemy import null
from sqlalchemy.orm import Query

from core.local_storage import queryes
from core.local_storage.db_enums import UserEvents
from core.local_storage.schema import *


class LocalStorage:

    def __init__(self):
        self.db = Path(__file__).parent.absolute().joinpath("control_bot.db")

    def connection(self):
        return aiosqlite.connect(self.db)

    async def upsert_user(
            self,
            tg_id: int,
            tg_username: str,
            name: Optional[str] = null(),
            phone: Optional[str] = null(),
            is_admin: Optional[bool] = False,
    ):

        async with self.connection() as db:

            user_exists = await self.get_user(tg_id)
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
            await db.execute(self._get_sql(query))
            await db.commit()
            return result

    async def get_user(self, tg_id: int) -> User:
        async with self.connection() as db:
            user_query = users_table.select().where(
                users_table.c.telegram_id == tg_id
            )
            user = await db.execute(self._get_sql(user_query))
            user = await user.fetchone()
            if user:
                user = User(*user)
            return user

    async def get_all_users(self):
        # TODO: generator
        async with self.connection() as db:
            users_query = users_table.select()
            users = await db.execute(self._get_sql(users_query))
            users = await users.fetchall()
            users = [User(*user) for user in users]
            return users

    async def get_admins(self) -> List[User]:
        async with self.connection() as db:
            admins_query = users_table.select().where(
                users_table.c.is_admin == 1
            )
            admins = await db.execute(self._get_sql(admins_query))
            admins = await admins.fetchall()
            admins = [User(*admin) for admin in admins]
            return admins

    async def save_channel(self, name: str):
        async with self.connection() as db:
            query: Query = channel_table.insert().values({
                'name': name
            })
            await db.execute(self._get_sql(query))
            await db.commit()

    async def get_subscribers(self, channel: str) -> List[User]:
        async with self.connection() as db:
            subscribers_query = queryes.get_subscribers(channel)
            subscribers = await db.execute(self._get_sql(subscribers_query))
            subscribers = await subscribers.fetchall()
            subscribers = [User(*subs) for subs in subscribers]
            return subscribers

    async def channel_subscribe(self, user_telegram_id: int, channel: str) -> bool:
        async with self.connection() as db:
            subscribe_query = channels_users_associations.insert().values({
                "user_id": queryes.get_user_id_query(user_telegram_id),
                "channel_id": queryes.get_channel_id_query(channel)
            })
            result = await db.execute(self._get_sql(subscribe_query))
            await db.commit()
        return bool(result.rowcount)

    async def channel_unsubscribe(self, user_telegram_id: int, channel: str) -> bool:
        async with self.connection() as db:
            unsubscribe_query = queryes.get_unsubscribe_query(user_telegram_id, channel)
            result = await db.execute(self._get_sql(unsubscribe_query))
            await db.commit()
        return bool(result.rowcount)

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
    user = asyncio.run(store.get_user(172698654))
    admins = asyncio.run(store.get_admins())
    print(user)
    print(admins)
    # asyncio.run(store.save_channel('123'))

# id
# name
# phone
# username
# telegram_id