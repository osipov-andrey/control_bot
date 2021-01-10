from sqlalchemy import create_engine

import local_storage


engine = create_engine('sqlite:///control_bot.db')


def create_tables():
    local_storage.users_table.create(engine, checkfirst=True)
    local_storage.channel_table.create(engine, checkfirst=True)
    local_storage.channels_users_associations.create(engine, checkfirst=True)


# async def create_super_user(telegram_id):


if __name__ == '__main__':
    create_tables()
