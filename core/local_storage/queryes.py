from typing import Optional

from sqlalchemy import null, select, delete, insert, update, and_
from sqlalchemy.sql import Select, Delete, Insert, Update

from core.local_storage.schema import actuators_table, actuators_users_associations, channel_table, \
    channels_users_associations, \
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


def get_actuator_id_query(
        actuator_name: str
) -> Select:
    query = select(
        [actuators_table.c.id, ]
    ).where(
        actuators_table.c.name == actuator_name
    )
    return query


def grant_query(
        tg_id: int,
        actuator_name: str
) -> Insert:
    """ Дать пользователю права на актуатор """
    user_id_query = get_user_id_query(tg_id)
    actuator_id_query = get_actuator_id_query(actuator_name)
    insert_query = insert(actuators_users_associations).values({
        "user_id": user_id_query,
        "actuator_id": actuator_id_query
    })
    return insert_query


def revoke_query(
        tg_id: int,
        actuator_name: str
) -> Delete:
    """ Забрать у пользователю права на актуатор """
    user_id_query = get_user_id_query(tg_id)
    actuator_id_query = get_actuator_id_query(actuator_name)
    delete_query = delete(actuators_users_associations).where(and_(
        actuators_users_associations.c.user_id == user_id_query,
        actuators_users_associations.c.actuator_id == actuator_id_query
    ))
    return delete_query


def get_granters_query(
        actuator_name: str
) -> Select:
    """ Получить всех пользователей с доступом к актуатору """
    users_id_query = select(
        [actuators_users_associations.c.user_id, ]
    ).where(
        actuators_users_associations.c.actuator_id == get_actuator_id_query(actuator_name)
    )
    granters_query = select(users_table).where(
        users_table.c.id.in_(users_id_query)
    )
    return granters_query


def get_has_grant_query(
        tg_id: int,
        actuator_name: str
) -> Select:
    """ Есть ли у пользователя доступ к актуатору """
    has_grant_query = select(actuators_users_associations.c).where(and_(
        actuators_users_associations.c.user_id == get_user_id_query(tg_id),
        actuators_users_associations.c.actuator_id == get_actuator_id_query(actuator_name)
    ))
    return has_grant_query
