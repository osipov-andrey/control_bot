import aiogram
import logging

from core.bot.telegram_api import telegram_api_dispatcher as d
from core._helpers import get_log_cover
from core.bot._helpers import MenuTextButton
# from core.observer import Observer

from .handlers import *

_LOGGER = logging.getLogger(__name__)


class ControlBot:
    # MAIN_MENU = [
    #     MenuTextButton("help", "справка по командам бота"),
    #     MenuTextButton("me", "My telegram ID"),
    # ]

    def __init__(self, observer):
        d.observer = observer
        self.observer = observer
        self.bot_dispatcher = d

    # async def various_cmd_handler(self, message: aiogram.types.Message):
    #     _LOGGER.info(
    #         get_log_cover("Get message"),
    #         message.text + '\n' + str(message.from_user)
    #     )
    #     if not message.text.startswith('/'):  # Not a command
    #         return
    #
    #     main_command = message.text.split('_')[0][1:]
    #
    #     if main_command in self.observer.active_clients:
    #         bot_message = TelegramBotCommand(message.text, message.from_user)
    #         result = await self.observer.handle_command(bot_message)
    #         await message.reply(result)
    #     elif main_command == "getAvailableMethods":
    #         bot_message = TelegramBotCommand(message.text, message.from_user)
    #         await self.observer.save_new_client(bot_message)
    #     else:
    #         result = await self.main_menu_handler(main_command)
    #         await message.reply(result)

    async def send_message(self, *, chat_id, text, **kwargs):
        await self.bot_dispatcher.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    # async def main_menu_handler(self, cmd):
    #     if cmd == "help":
    #         return self.main_menu
    #
    #     return "main_kekos"
    #
    # @property
    # def main_menu(self):
    #     menu = "\n".join(
    #         f"/{command.cmd} - {command.description}"
    #         for command in self.MAIN_MENU
    #     ) + "\n" + "\n".join(f"/{client}" for client in self.observer.active_clients.keys())
    #     return menu
