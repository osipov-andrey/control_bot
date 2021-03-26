import asyncio
import logging
from abc import ABC
from typing import List, Type

from core import exceptions
from core.bot import emojies
from core.config import config
from core.inbox.models import TargetType, ActuatorMessage
from core.inbox.messages import OutgoingMessage
from core.mediator.dependency import MediatorDependency
from core.exceptions import NoSuchUser
from core.repository.repository import Channel, Repository, User
from core.sse.sse_event import SSEEvent


__all__ = ["ActuatorsInterface", "ChannelsInterface", "UsersInterface"]

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(config)


class BaseInterface(ABC):
    def __init__(self):
        self.db: Repository = Repository()


class ActuatorsInterface(BaseInterface, MediatorDependency):
    def __init__(self, memory_storage):
        super().__init__()
        self.memory_storage = memory_storage
        self.connected_actuators = dict()

    def is_connected(self, actuator_name) -> bool:
        return actuator_name in self.connected_actuators.keys()

    def save_actuator_info(self, message: ActuatorMessage):
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

    async def turn_on_actuator(self, actuator_name: str) -> asyncio.Queue:
        """ Turn on the actuator  """
        admins = await self.mediator.users.get_admins()
        if self.is_connected(actuator_name):
            text = f"{emojies.ACTUATOR_ALREADY_TURNED_ON} Actuator {actuator_name} already turned ON!"
            users = admins
            result = None
        else:
            actuator_queue: asyncio.Queue = asyncio.Queue()
            self.connected_actuators[actuator_name] = actuator_queue
            granters = await self.get_granters(actuator_name)
            users = set(admins + granters)
            text = f"{emojies.ACTUATOR_TURNED_ON} Actuator {actuator_name} has been turned ON!"
            result = actuator_queue

        for user in users:
            message = OutgoingMessage(chat_id=user.telegram_id, text=text)
            await self.mediator.send(message)
        if result:
            return result
        else:
            raise exceptions.ActuatorAlreadyConnected

    async def turn_off_actuator(self, actuator_name: str):
        """ Turn off the actuator """
        self.connected_actuators.pop(actuator_name)
        self.memory_storage.remove_client(actuator_name)
        admins = await self.mediator.users.get_admins()
        granters = await self.get_granters(actuator_name)
        for user in set(admins + granters):
            message = OutgoingMessage(
                chat_id=user.telegram_id,
                text=f"{emojies.ACTUATOR_TURNED_OFF} Actuator {actuator_name} has been turned OFF!",
            )
            await self.mediator.send(message)


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
    async def upsert(self, **kwargs):
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
