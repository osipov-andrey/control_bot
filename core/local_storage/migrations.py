from sqlalchemy import create_engine

import local_storage


TABLES = [
    local_storage.users_table,
    local_storage.channel_table,
    local_storage.channels_users_associations,
    local_storage.actuators_users_associations,
    local_storage.actuators_table
]


def create_tables():
    engine = create_engine('sqlite:///control_bot.db')
    for table in TABLES:
        table.create(engine, checkfirst=True)


if __name__ == '__main__':
    create_tables()
