from aiogram import types

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.db_enums import UserEvents
from core.local_storage.local_storage import LocalStorage


@d.message_handler(commands=["start"])
async def main_menu_handler(message: types.Message):
    db: LocalStorage = d.observer.db
    admins = await db.get_admins()
    if not admins:
        await db.upsert_user(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            name=message.from_user.full_name,
            is_admin=True
        )
        await message.answer("Теперь вы администратор бота")
        return

    clients = [
        MenuTextButton(client, "-")
        for client in d.observer.active_clients.keys()
    ]
    menu = get_menu(
        header="Список команд:",
        commands=[
            MenuTextButton("start", "главное меню"),
            MenuTextButton("users", "операции с пользователями"),
            MenuTextButton("me", "личный кабинет"),
            # MenuTextButton("all_users", "Список пользователей"),
        ] + clients
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
