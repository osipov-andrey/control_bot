from aiogram import types

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.telegram_api import telegram_api_dispatcher as d


@d.message_handler(commands=["start"])
async def main_menu_handler(message: types.Message):

    menu = get_menu(
        header="Список команд:",
        commands=[
            MenuTextButton("start", "главное меню"),
            MenuTextButton("me", "узнать свой телеграм ID"),
        ]
    )
    # if db.superuser.is_admin(message["from"]["id"]):
    #     superuser_cmds = [
    #         "/users - Просмотреть список пользователей",
    #         "/channel - Операции с каналами",
    #         "/client - Операции с клиентами",
    #     ]
    #     cmds += superuser_cmds
    # cmds += db.grants.clients_by_user_id("", str(message["from"]["id"]))
    await message.answer(menu)
