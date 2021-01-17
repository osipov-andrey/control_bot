from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetTypes
from core.bot._helpers import get_menu, MenuTextButton
from core.bot.handlers.main_menu.users_commands import get_subscribe_cmd
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.local_storage import LocalStorage


@d.message_handler(commands=["users"])
async def users_handler(message: types.Message):
    await MainMenu.users.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
                     MenuTextButton("all_users", "Список пользователей"),
                     MenuTextButton("subscribe", "Подписать пользователя на канал"),
                 ]
    )
    await message.answer(menu)


@d.message_handler(commands=["all_users"], state=MainMenu.users)
async def all_users_handler(message: types.Message, state: FSMContext):
    db: LocalStorage = d.observer.db
    users = await db.get_all_users()
    await message.answer(users)


@d.message_handler(commands=["subscribe"], state=MainMenu.users)
async def subscribe_handler(message: types.Message, state: FSMContext):

    user_id = message.chat.id
    is_admin = True
    cmd = "subscribe"
    subscribe_cmd = get_subscribe_cmd(cmd, user_id, is_admin)

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()
    }
    from core.bot import CommandFillStatus

    async def callback(*args, **kwargs):
        print(args)
        print(kwargs)

    from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow
    await start_cmd_internal_workflow(
        state, subscribe_cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )
