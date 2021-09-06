from pathlib import Path
from typing import List

import pytest
from core.repository import User, Base, Channel

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Faker.seed(0)
fake = Faker()

users = [
    User(
        **dict(
            id=fake.unique.random_int(),
            telegram_id=fake.iana_id(),
            telegram_username=fake.user_name(),
            name=fake.name(),
            is_admin=False,
        )
    )
    for _ in range(10)
]

channels = [
    Channel(
        **dict(
            id=fake.unique.random_int(), name=fake.domain_word(), description=fake.catch_phrase()
        )
    )
    for _ in range(5)
]

PATH_TO_DB = Path(__file__).parent.absolute().joinpath("test.sqlite")

engine = create_engine(  # We can't create DB with async engine
    f"sqlite:///{str(PATH_TO_DB)}",
    echo=True,
)
Session = scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope="session")
def test_database() -> Session:
    Base.metadata.create_all(engine)
    session = Session()

    _add_users(session, users)
    _add_channels(session, channels)

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _add_users(session: Session, users_: List[User]) -> None:
    session.add_all(users_)


def _add_channels(session: Session, channels_: List[Channel]) -> None:
    session.add_all(channels_)
