from sqlalchemy import select, delete, and_
from sqlalchemy.sql import Select, Delete

from core.local_storage.schema import channel_table, channels_users_associations, users_table


def get_channel_id_query(channel_name: str) -> Select:
    query = select(
        [channel_table.c.id, ]
    ).where(
        channel_table.c.name == channel_name
    )
    return query


def get_user_id_query(user_telegram_id: int) -> Select:
    query = select(
        [users_table.c.id, ]
    ).where(
        users_table.c.telegram_id == user_telegram_id
    )
    return query


def get_unsubscribe_query(user_telegram_id: int, channel_name: str) -> Delete:
    query = delete(channels_users_associations).where(and_(
        channels_users_associations.c.channel_id == get_channel_id_query(channel_name),
        channels_users_associations.c.user_id == get_user_id_query(user_telegram_id)
    ))
    return query
