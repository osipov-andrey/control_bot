import argparse
import asyncio
from logging.config import dictConfig

import aiogram

from core.mediator import Mediator, MediatorDependency
from . import config

from core.bot.telegram_api import telegram_api_dispatcher
from core.inbox.consumers.rabbit import RabbitConsumer
from core.inbox.dispatcher import InboxDispatcher

dictConfig(config.config["logging"])


def run():
    mediator = Mediator(telegram_api_dispatcher)

    inbox_queue = asyncio.Queue()
    inbox_dispatcher = InboxDispatcher(mediator, inbox_queue)
    rabbit = RabbitConsumer(**config.config["rabbit"], inbox_queue=inbox_queue)

    MediatorDependency.add_mediator(mediator)

    asyncio.ensure_future(rabbit.listen_to_rabbit())
    asyncio.ensure_future(inbox_dispatcher.message_dispatcher())
    aiogram.executor.start_polling(telegram_api_dispatcher, skip_updates=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="Bot")
    subparsers = parser.add_subparsers(help="Operating mode")
    parser_start = subparsers.add_parser("run", help="Run bot")
    parser_start.set_defaults(func=run)

    args = parser.parse_args()
    args.func()
