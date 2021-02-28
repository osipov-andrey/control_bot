import asyncio
import logging
from abc import ABC
from typing import List

from core.config import config
from core._helpers import TargetType
from core.inbox.messages import TextMessage
from core.repository.exceptions import NoSuchUser
from core.repository.repository import Channel, Repository, User
from core.sse.sse_event import SSEEvent


__all__ = [
    'ActuatorsInterface',
    'ChannelsInterface',
    'UsersInterface',
]

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(config)


class BaseInterface(ABC):

    def __init__(self):
        self.db = Repository()


class ActuatorsInterface(BaseInterface):

    def __init__(self, memory_storage):
        super().__init__()
        self.memory_storage = memory_storage
        self.connected_actuators = dict()

    def is_connected(self, actuator_name) -> bool:
        return actuator_name in self.connected_actuators.keys()

    def save_actuator_info(self, message: TextMessage):
        """ Сохранить логику актуатора в ОЗУ """
        actuator_name = message.target.target_name

        assert message.target.target_type == TargetType.SERVICE.value
        assert actuator_name in self.connected_actuators

        self.memory_storage.save_client(actuator_name, message.commands)

    def get_command_info(self, actuator_name: str, command: str):
        """ Получить информацию о команде актуатора """
        return self.memory_storage.get_command_info(actuator_name, command)

    def get_actuator_info(self, actuator_name: str):
        """ Получить информацию о всех командах актуатора """
        return self.memory_storage.get_client_info(actuator_name)

    def new_sse_connection(self, actuator_name: str) -> asyncio.Queue:
        """ Подключить к интерфейсу новый актуатор  """
        actuator_queue = asyncio.Queue()
        self.connected_actuators[actuator_name] = actuator_queue
        return actuator_queue

    async def create_actuator(self, actuator_name: str, description: str):
        return await self.db.create_actuator(actuator_name, description)

    async def delete_actuator(self, actuator_name: str):
        return await self.db.delete_actuator(actuator_name)

    async def emit_event(self, actuator_name: str, event: SSEEvent):
        """ Отправить ЕVENT в актуатор """
        try:
            actuator_queue: asyncio.Queue = self.connected_actuators[actuator_name]
            await actuator_queue.put(event)
        except KeyError:
            return "Unknown Client"

    async def grant(self, telegram_id: int, actuator_name: str):
        """ Предоставить пользователю доступ к актуатору """
        return await self.db.grant(telegram_id, actuator_name)

    async def revoke(self, telegram_id: int, actuator_name: str):
        """ Забрать у пользователя доступ к актуатору """
        return await self.db.revoke(telegram_id, actuator_name)

    async def get_all(self):
        """ Получить все зарегистрированные актуаторы """
        actuators = await self.db.get_actuators()
        return actuators

    async def get_granters(self, actuator_name: str):
        """ Получить пользователей с доступом к актуатору """
        granters = await self.db.get_granters(actuator_name)
        return granters

    def stop_sse_connection(self, actuator_name: str):
        """ Подключить актуатор от интерфейса """
        self.connected_actuators.pop(actuator_name)
        self.memory_storage.remove_client(actuator_name)


class ChannelsInterface(BaseInterface):

    async def all_channels(self) -> List[Channel]:
        return await self.db.all_channels()

    async def create_channel(self, channel: str, description: str) -> bool:
        return await self.db.save_channel(channel, description)

    async def delete_channel(self, channel: str) -> bool:
        return await self.db.delete_channel(channel)

    async def subscribe(self, user_telegram_id: int, channel: str):
        await self.db.channel_subscribe(user_telegram_id, channel)

    async def unsubscribe(self, user_telegram_id: int, channel: str):
        await self.db.channel_unsubscribe(user_telegram_id, channel)

    async def get_subscribers(self, channel: str) -> List[User]:
        subscribers = await self.db.get_subscribers(channel)
        return subscribers

    async def get_subscribes(self, user_telegram_id: int):
        channels = await self.db.get_user_subscribes(user_telegram_id)
        return channels


class UsersInterface(BaseInterface):

    async def upsert(
            self,
            **kwargs
    ):
        return await self.db.upsert_user(**kwargs)

    async def get_admins(self) -> List[User]:
        return await self.db.get_admins()

    async def is_admin(self, telegram_id: int) -> bool:
        """ Проверка админских прав у пользователя """
        try:
            user: User = await self.db.get_user(telegram_id)
        except NoSuchUser:
            return False
        return bool(user.is_admin)

    async def get_all(self) -> List[User]:
        """ Получить ВСЕХ пользователей """
        users = await self.db.get_all_users()
        return users

    async def subscribes(self, telegram_id: int) -> List[Channel]:
        """ Получить подписки пользователя """
        subs = await self.db.get_user_subscribes(telegram_id)
        return subs

    async def has_grant(self, telegram_id: int, actuator_name: str) -> bool:
        """ Есть ли у пользователя доступ к актутатору """
        result = await self.db.user_has_grant(telegram_id, actuator_name)
        return result
