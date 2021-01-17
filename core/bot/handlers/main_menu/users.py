from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetTypes
from core.bot._helpers import delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.handlers.main_menu.users_commands import get_subscribe_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.local_storage.local_storage import LocalStorage
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow


@d.message_handler(commands=["users"])
async def users_handler(message: types.Message):
    await MainMenu.users.set()
    menu = get_menu(
        header="Список команд: ",
        commands=[
                     MenuTextButton("all_users", "Список пользователей"),
                     MenuTextButton("subscribe", "Подписать пользователя на канал"),
                     MenuTextButton("unsubscribe", "Отписать пользователя от канала"),
                 ]
    )
    await message.answer(menu)


@d.message_handler(commands=["all_users"], state=MainMenu.users)
async def all_users_handler(message: types.Message, state: FSMContext):
    db: LocalStorage = d.observer.db
    users = await db.get_all_users()
    await message.answer(users)


@d.message_handler(commands=["subscribe", "unsubscribe"], state=MainMenu.users)
async def subscribe_handler(message: types.Message, state: FSMContext):

    user_id = message.chat.id
    is_admin = True
    cmd = delete_cmd_prefix(message.text)
    subscribe_cmd = get_subscribe_cmd(cmd, user_id, is_admin)

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()
    }

    async def subscribe_callback(**kwargs):
        user_to_subs_id = kwargs.get("user_id")
        channel = kwargs.get("channel")
        await d.observer.channel_subscribe(user_to_subs_id, channel)
        await message.answer(f"Пользователь {user_to_subs_id} подписан на канал {channel}")

    async def unsubscribe_callback(**kwargs):
        user_to_subs_id = kwargs.get("user_id")
        channel = kwargs.get("channel")
        #TODO:
        # await d.observer.db.unsubscribe_user_on_channel(user_to_subs_id, channel)
        await message.answer(f"Пользователь {user_to_subs_id} отписан от канала {channel}")

    if cmd == "subscribe":
        callback = subscribe_callback
    else:
        callback = unsubscribe_callback

    await start_cmd_internal_workflow(
        state, subscribe_cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )
