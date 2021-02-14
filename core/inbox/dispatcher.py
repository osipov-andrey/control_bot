import logging
from asyncio import Queue
from typing import Iterable

from .._constants import INTRO_COMMAND
from .._helpers import Issue, MessageTarget
from ..inbox.messages import BaseMessage, TargetTypes, message_fabric


_LOGGER = logging.getLogger(__name__)


class InboxDispatcher:

    def __init__(self, observer, queue: Queue):
        self.observer = observer
        self.queue = queue

    async def message_dispatcher(self):
        while True:
            message: BaseMessage = await self.queue.get()
            self.queue.task_done()
            _LOGGER.info("Get message: %s", message)
            await self.dispatch(message)

    async def dispatch(self, message: BaseMessage):
        # TODO if target.message_id: ...
        if message.cmd == INTRO_COMMAND:
            self.observer.actuators.save_actuator_info(message)
            return

        if message.target.target_type == TargetTypes.USER.value:
            result_message = await self.observer.send(message)
            result_id = result_message.message_id

            await self._check_replies(message, result_id)
            await self._check_issue(message, result_id)

        if message.target.target_type == TargetTypes.CHANNEL.value:
            channel = message.target.target_name
            subscribers: Iterable = await self.observer.channels.get_subscribers(channel)

            for subs in subscribers:
                # TODO некрасиво это все
                new_target = MessageTarget(
                    target_type=TargetTypes.USER.value,
                    target_name=subs,
                    message_id=message.target.message_id
                )
                new_message_dict = dict(message.__dict__)
                new_message_dict["target"] = new_target._asdict()
                new_message_dict["text"] = f"Channel <b>{channel}</b>\n" + new_message_dict["text"]
                new_message = message_fabric(new_message_dict)
                await self.dispatch(new_message)

    async def _check_replies(self, message: BaseMessage, reply_to_message_id: int):
        if message.replies:
            replies = message.prepare_replies(reply_to_message_id)
            for reply in replies:
                await self.dispatch(reply)

    async def _check_issue(self, message: BaseMessage, reply_to_message_id: int):
        if message.issue and (message.issue["resolved"] is False):
            # Устанавливаем проблемные события с указанным ID сообщения,
            # на которое должно будет ответить сообщение с решением проблемы
            issue = Issue(**message.issue, reply_to_message_id=reply_to_message_id)
            self.observer.memory_storage.set_issue(issue)
            # 'Разрешение' issues происходит при создании сообщения
