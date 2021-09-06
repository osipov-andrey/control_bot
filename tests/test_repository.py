from pathlib import Path

import pytest
from core.repository import Repository, Base, User
from core.repository.repository import first
from sqlalchemy import create_engine
from sqlalchemy.engine import Row
from sqlalchemy.future import select
from sqlalchemy.orm import scoped_session, sessionmaker


PATH_TO_DB = Path(__file__).parent.absolute().joinpath("test.sqlite")

repository = Repository(path_to_db=PATH_TO_DB)
engine = create_engine(  # We can't create DB with async engine
    f"sqlite:///{str(PATH_TO_DB)}",
    echo=True,
)
Session = scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope="function")
def db_session() -> Session:
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_insert_user(db_session: Session):
    await repository.upsert_user(tg_id=1012, tg_username="kek_lol2")
    user_result: Row[User] = db_session.execute(
        select(User).where(User.telegram_id == 1012)
    ).first()
    user: User = first(user_result)
    assert user.telegram_username == "kek_lol2"
