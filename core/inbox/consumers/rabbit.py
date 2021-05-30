import asyncio
import aioamqp
import json
import logging

import pydantic
from aioamqp.channel import Channel
from core.config import config

from ..models import ActuatorMessage

_LOGGER = logging.getLogger(__name__)


class RabbitConsumer:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        login: str,
        pwd: str,
        rabbit_queue: str,
        inbox_queue: asyncio.Queue
    ):

        self.host = host
        self.port = port
        self.login = login
        self.password = pwd
        self.rabbit_queue = rabbit_queue
        self.inbox_queue = inbox_queue

    async def listen_to_rabbit(self):

        transport, protocol = await aioamqp.connect(
            self.host,
            self.port,
            login=self.login,
            password=self.password,
            login_method="PLAIN",
        )

        channel: Channel = await protocol.channel()
        await channel.queue_declare(config["rabbit"]["rabbit_queue"], durable=True)
        await channel.basic_consume(self._callback, queue_name=self.rabbit_queue, no_ack=True)

    async def _callback(self, channel, body, envelope, properties):
        _LOGGER.info("Get message from rabbit: %s", body)
        body = body.decode()
        body = json.loads(body)
        try:
            message = ActuatorMessage(**body)
        except pydantic.ValidationError as e:
            _LOGGER.error("Validation error! %s", e.json())
            raise
        await self.inbox_queue.put(message)
