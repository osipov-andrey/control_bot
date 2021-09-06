import random
from typing import List

from core.repository import Repository, User
from core.repository.repository import first
from sqlalchemy.engine import Row
from sqlalchemy.future import select


from tests.conftest import PATH_TO_DB, Session, users

repository = Repository(path_to_db=PATH_TO_DB)


def test_add_users(test_database: Session):
    checking_user: User = random.choice(users)
    user_result: Row[User] = test_database.execute(
        select(User).where(User.id == checking_user.id)
    ).first()
    user: User = first(user_result)
    assert user.id == checking_user.id


def insert_users(users_: List[User]) -> None:
    ...
