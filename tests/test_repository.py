import random
from typing import List

from core.repository import Repository, User, Channel
from core.repository.repository import first
from sqlalchemy.engine import Row
from sqlalchemy.future import select


from tests.conftest import PATH_TO_DB, Session, users, channels

repository = Repository(path_to_db=PATH_TO_DB)


class TestTestDatabase:
    def test_add_users(self, test_database: Session):
        checking_user: User = random.choice(users)
        user_result: Row[User] = test_database.execute(
            select(User).where(User.id == checking_user.id)
        ).first()
        user: User = first(user_result)
        assert user.id == checking_user.id

    def test_add_channels(self, test_database: Session):
        checking_channel: Channel = random.choice(channels)
        channel_result: Row[Channel] = test_database.execute(
            select(Channel).where(Channel.id == checking_channel.id)
        ).first()
        channel: Channel = first(channel_result)
        assert channel.id == checking_channel.id


def insert_users(users_: List[User]) -> None:
    ...
