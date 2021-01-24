from typing import Optional

from sqlalchemy import null, select, delete, insert, update, and_
from sqlalchemy.sql import Select, Delete, Insert, Update

from core.local_storage.schema import actuators_table, channel_table, channels_users_associations, \
    users_table


def get_channel_id_query(channel_name: str) -> Select:
    """ ID канала по названию """
    query = select(
        [channel_table.c.id, ]
    ).where(
        channel_table.c.name == channel_name
    )
    return query


def get_user_id_query(user_telegram_id: int) -> Select:
    """ ID пользователя по telegram_id """
    query = select(
        [users_table.c.id, ]
    ).where(
        users_table.c.telegram_id == user_telegram_id
    )
    return query


def get_unsubscribe_query(user_telegram_id: int, channel_name: str) -> Delete:
    """ Отписать пользователя от канала """
    query = delete(channels_users_associations).where(and_(
        channels_users_associations.c.channel_id == get_channel_id_query(channel_name),
        channels_users_associations.c.user_id == get_user_id_query(user_telegram_id)
    ))
    return query


def get_subscribers(channel_name: str) -> Select:
    """ Получить подписчиков канала """
    channel_id_query = select(
        [channel_table.c.id, ]
    ).where(
        channel_table.c.name == channel_name
    )

    users_id_query = select(
        [channels_users_associations.c.user_id, ]
    ).where(
        channels_users_associations.c.channel_id == channel_id_query
    )

    subscribers_query = select(
        [users_table.c.telegram_id, ],
        users_table.c.id.in_(users_id_query)
    )
    return subscribers_query


def insert_user(
        tg_id: int,
        tg_username: str,
        name: Optional[str] = null(),
        phone: Optional[str] = null(),
        is_admin: Optional[bool] = False,
) -> Insert:
    """ Сохранить пользователя """
    insert_query = insert(users_table).values(
        {
            "telegram_id": tg_id,
            "telegram_username": tg_username,
            "name": name,
            "phone_number": phone,
            "is_admin": is_admin
        }
    )
    return insert_query


def update_user(
        tg_id: int,
        tg_username: str,
        name: Optional[str] = null(),
        phone: Optional[str] = null(),
        is_admin: Optional[bool] = False,
) -> Update:
    """ Обновить пользователя """
    update_query = update(users_table).values({
        "name": name,
        "phone_number": phone,
        "is_admin": is_admin
    }).where(
        users_table.c.telegram_id == tg_id
        or users_table.c.telegram_username == tg_username
    )
    return update_query


def create_actuator_query(
        name: str,
        description: Optional[str] = None
) -> Insert:
    """ Создать актуатор """
    insert_query = insert(actuators_table).values({
        "name": name,
        "description": description
    })
    return insert_query


def delete_actuator_query(
        name: str
) -> Delete:
    """ Удалить актуатор """
    delete_query = delete(actuators_table).where(
        actuators_table.c.name == name
    )
    return delete_query


