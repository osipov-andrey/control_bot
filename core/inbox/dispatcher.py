import logging
from asyncio import Queue
from typing import Iterable, Union

from core.inbox.models import Issue, MessageTarget, TargetType, ActuatorMessage
from core.inbox.messages import OutgoingMessage, create_message_from_inbox


_LOGGER = logging.getLogger(__name__)

INTRO_COMMAND = "getAvailableMethods"


class InboxDispatcher:
    def __init__(self, observer, queue: Queue):
        self.observer = observer
        self.queue = queue

    async def message_dispatcher(self):
        while True:
            message: ActuatorMessage = await self.queue.get()
            self.queue.task_done()
            _LOGGER.info("Get message: %s", message)
            await self.dispatch(message)

    async def dispatch(self, message: ActuatorMessage):
        message_type: str = message.target.target_type
        if message_type == TargetType.SERVICE.value:
            await self.handle_service_message(message)
        elif message_type == TargetType.USER.value:
            await self.handle_user_message(message)
        elif message_type == TargetType.CHANNEL.value:
            await self.handle_channel_message(message)

    async def handle_service_message(self, telegram_message: ActuatorMessage):
        if telegram_message.cmd == INTRO_COMMAND:
            self.observer.actuators.save_actuator_info(telegram_message)

    async def handle_user_message(self, message: Union[ActuatorMessage, OutgoingMessage]):
        if isinstance(message, ActuatorMessage):
            outgoing_message = create_message_from_inbox(message)
        else:
            outgoing_message = message
        result_message = await self.observer.send(outgoing_message)
        result_id = result_message.message_id
        if outgoing_message.replies:
            await self._check_replies(outgoing_message, result_id)
        if outgoing_message.issue:
            await self._check_issue(message, result_id)

    async def handle_channel_message(self, message: ActuatorMessage):
        channel = message.target.target_name
        subscribers: Iterable = await self.observer.channels.get_subscribers(channel)
        new_text = f"Channel <b>{channel}</b>\n" + message.text
        for subs in subscribers:
            new_target = MessageTarget(
                target_type=TargetType.USER.value,
                target_name=subs.telegram_id,
                message_id=message.target.message_id,
            )
            outgoing_message = create_message_from_inbox(message, target=new_target, text=new_text)
            await self.handle_user_message(outgoing_message)

    async def _check_replies(self, message: OutgoingMessage, reply_to_message_id: int):
        if message.replies:
            replies = message.get_replies(reply_to_message_id)
            for reply in replies:
                await self.handle_user_message(reply)  # TODO replies for channel

    async def _check_issue(self, message: ActuatorMessage, reply_to_message_id: int):
        if message.issue and (message.issue.resolved is False):
            # Устанавливаем проблемные события с указанным ID сообщения,
            # на которое должно будет ответить сообщение с решением проблемы
            issue = message.issue
            issue.reply_to_message_id = reply_to_message_id
            self.observer.memory_storage.set_issue(issue)
            # 'Разрешение' issues происходит при создании сообщения
