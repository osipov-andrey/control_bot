from aiogram import types

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.telegram_api import telegram_api_dispatcher


@telegram_api_dispatcher.message_handler(commands=["start"])
async def main_menu_handler(message: types.Message):
    observer = telegram_api_dispatcher.observer

    admins = await observer.users.get_admins()
    if not admins:
        await observer.users.upsert(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            name=message.from_user.full_name,
            is_admin=True
        )
        await message.answer("Теперь вы администратор бота")
        return

    actuators = [
        MenuTextButton(client, "-")
        for client in observer.actuators.connected_actuators.keys()
    ]
    menu = get_menu(
        header="Список команд:",
        commands=[
            MenuTextButton("start", "главное меню"),
            MenuTextButton("users", "операции с пользователями"),
            MenuTextButton("me", "личный кабинет"),
            # MenuTextButton("all_users", "Список пользователей"),
        ] + actuators
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
