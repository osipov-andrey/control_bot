import asyncio

from sqlalchemy.future import select

from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    telegram_username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    uq_id_user = UniqueConstraint("telegram_id", "telegram_username", name="uq_id_user")

    def __str__(self):
        return f"{self.telegram_username} : {self.telegram_id}"


async def async_main():
    engine = create_async_engine(
        "sqlite+aiosqlite:///control_bot.sqlite",
        echo=True,
    )

    async with AsyncSession(engine) as session:
        async with session.begin():
            users = await session.execute(select(User).order_by(User.id))

            for user in users.scalars():
                print(user)

            session.add(User(telegram_username="Ers1rhd", telegram_id=1726986541))


asyncio.run(async_main())
