import logging
from asyncio import Queue

from core._constants import INTRO_COMMAND
from core.inbox.messages import BaseMessage, TargetTypes

_LOGGER = logging.getLogger(__name__)


class RabbitDispatcher:

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
        if message.cmd == INTRO_COMMAND:
            self.observer.save_client_info(message)
        elif message.target.target_type == TargetTypes.USER.value:
            result_message = await self.observer.send(message)
            if message.replies:
                replies = message.prepare_replies(result_message.message_id)
                for reply in replies:
                    await self.dispatch(reply)
