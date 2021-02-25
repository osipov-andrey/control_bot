from sqlalchemy import create_engine

from . import repository


TABLES = [
    repository.users_table,
    repository.channel_table,
    repository.channels_users_associations,
    repository.actuators_users_associations,
    repository.actuators_table
]


def create_tables():
    engine = create_engine(f'sqlite:///{repository.PATH_TO_DB}')
    for table in TABLES:
        table.create(engine, checkfirst=True)


if __name__ == '__main__':
    create_tables()
