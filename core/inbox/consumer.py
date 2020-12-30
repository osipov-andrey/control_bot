import asyncio

import aioamqp
import json

from aioamqp.channel import Channel

from core.inbox._helpers import MessageTarget


class MessageTargetDescriptor:

    def __set__(self, instance: 'TelegramLeverMessage', value: dict):
        instance.__dict__["target"] = MessageTarget(**value)


class TelegramLeverMessage:
    target = MessageTargetDescriptor()

    def __init__(self, raw_message: bytes):
        message_body = raw_message.decode()
        message_body = json.loads(message_body)
        for key, value in message_body.items():
            setattr(self, key, value)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __str__(self):
        values = '\n'.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f"\n{'#'*20} TelegramLeverMessage {'#'*20}" \
               f"\n{values}" \
               f"\n{'#'*20}{' '*22}{'#'*20}"


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
            self.host, self.port,
            login=self.login, password=self.password, login_method='PLAIN'
        )
        channel: Channel = await protocol.channel()

        while True:
            await channel.basic_consume(self._callback, queue_name=self.rabbit_queue, no_ack=True)

    async def _callback(self, channel, body, envelope, properties):
        message = TelegramLeverMessage(body)
        await self.inbox_queue.put(message)

