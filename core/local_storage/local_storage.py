import asyncio

from pathlib import Path
from typing import List, Optional

import aiosqlite
from sqlalchemy import null
from sqlalchemy.orm import Query

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