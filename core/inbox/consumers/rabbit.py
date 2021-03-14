import asyncio
import aioamqp
import json
import logging

from aioamqp.channel import Channel

from ..messages import inbox_message_fabric


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
        for trying in range(5):
            try:
                transport, protocol = await aioamqp.connect(
                    self.host, self.port,
                    login=self.login, password=self.password, login_method='PLAIN'
                )
            except ConnectionError as err:
                await asyncio.sleep(1)
                if trying == 4:
                    raise err
                continue

        channel: Channel = await protocol.channel()
        await channel.queue_declare("telegram", durable=True)
        await channel.basic_consume(self._callback, queue_name=self.rabbit_queue, no_ack=True)

    async def _callback(self, channel, body, envelope, properties):
        _LOGGER.info("Get message from rabbit: %s", body)
        body = body.decode()
        body = json.loads(body)
        message = inbox_message_fabric(body)
        await self.inbox_queue.put(message)
