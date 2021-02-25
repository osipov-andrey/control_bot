from dataclasses import asdict

from aiogram import types
from aiogram.dispatcher import FSMContext

from core._helpers import MessageTarget, TargetType
from core.bot._helpers import admin_only_method, delete_cmd_prefix, get_menu, MenuTextButton
from core.bot.constant_strings import UNKNOWN_COMMAND
from core.bot.handlers._static_commands import *
from core.bot.handlers.main_menu.users_commands import get_grant_or_revoke_cmd, \
    get_subscribe_or_unsubscribe_cmd
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.repository.exceptions import AlreadyHasItException
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow
from core.bot.handlers._base_handler import MessageHandler


@d.class_message_handler(commands=[USERS])
class UsersHandler(MessageHandler):

    @admin_only_method
    async def execute(self, message: types.Message, state: FSMContext, **kwargs):
        await MainMenu.users.set()
        menu = get_menu(
            header="Users commands: ",
            commands=[
                MenuTextButton(ALL_USERS, "All bot users"),
                MenuTextButton(SUBSCRIBE, "Subscribe user to channel"),
                MenuTextButton(UNSUBSCRIBE, "Unsubscribe user from channel"),
                MenuTextButton(GRANT, "Grant user to actuator"),
                MenuTextButton(REVOKE, "Revoke user from actuator"),
            ]
        )
        await message.answer(menu)


@d.class_message_handler(commands=[ALL_USERS], state=MainMenu.users)
class AllUsersHandler(MessageHandler):
    async def execute(self, message: types.Message, state: FSMContext, **kwargs):
        users = await self.mediator.users.get_all()
        await message.answer(users)


@d.class_message_handler(commands=[SUBSCRIBE], state=[MainMenu.users, MainMenu.channels])
class SubscribeHandler(MessageHandler):
    async def execute(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_subscribe_or_unsubscribe_cmd(SUBSCRIBE, self.user_telegram_id, self.is_admin)

        message_kwargs = {
            "target": asdict(MessageTarget(TargetType.USER.value, self.user_telegram_id))
        }

        async def subscribe_callback(**kwargs_):
            user_to_subs_id = kwargs_.get("user_id")
            channel = kwargs_.get("channel")
            try:
                await self.mediator.channels.subscribe(user_to_subs_id, channel)
            except AlreadyHasItException:
                await message.answer(f"The user {user_to_subs_id} is ALREADY subscribed to the channel {channel}")
            else:
                await message.answer(f"The user {user_to_subs_id} is subscribed to the channel {channel}")

        await start_cmd_internal_workflow(
            state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=subscribe_callback
        )


@d.class_message_handler(commands=[UNSUBSCRIBE], state=[MainMenu.users, MainMenu.channels])
class SubscribeHandler(MessageHandler):
    async def execute(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_subscribe_or_unsubscribe_cmd(UNSUBSCRIBE, self.user_telegram_id, self.is_admin)

        message_kwargs = {
            "target": asdict(MessageTarget(TargetType.USER.value, self.user_telegram_id))
        }

        async def unsubscribe_callback(**kwargs_):
            user_to_subs_id = kwargs_.get("user_id")
            channel = kwargs_.get("channel")
            await self.mediator.channels.unsubscribe(user_to_subs_id, channel)
            await message.answer(f"The user {user_to_subs_id} unsubscribed from channel {channel}")

        await start_cmd_internal_workflow(
            state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=unsubscribe_callback
        )


@d.message_handler(commands=[GRANT, REVOKE], state=[MainMenu.users, MainMenu.actuators])
async def grant_handler(message: types.Message, state: FSMContext):
    from mediator import mediator
    user_id = message.chat.id
    is_admin = True  # в state=MainMenu.users может попасть только админ
    cmd_text = delete_cmd_prefix(message.text)
    cmd = await get_grant_or_revoke_cmd(cmd_text, user_id, is_admin)

    message_kwargs = {
        "target": asdict(MessageTarget(TargetType.USER.value, user_id))
    }

    async def grant_callback(**kwargs):
        user_to_grant_id = kwargs.get("user_id")
        actuator = kwargs.get("actuator")
        try:
            await mediator.actuators.grant(user_to_grant_id, actuator)
            answer = f"User {user_to_grant_id} gained grant to {actuator}"
        except AlreadyHasItException:
            answer = f"User {user_to_grant_id} ALREADY has grant to {actuator}"
        # except NoSuchUser:
        #     answer = "Неизвестный пользователь"
        await message.answer(answer)

    async def revoke_callback(**kwargs):
        user_to_revoke_id = kwargs.get("user_id")
        actuator = kwargs.get("actuator")
        # try:
        await mediator.actuators.revoke(user_to_revoke_id, actuator)
        await message.answer(f"User {user_to_revoke_id} revoke from {actuator}")
        # except NoSuchUser:
        #     await message.answer("Неизвестный пользователь")

    if cmd_text == GRANT:
        callback = grant_callback
    elif cmd_text == REVOKE:
        callback = revoke_callback
    else:
        await message.answer(text=UNKNOWN_COMMAND)
        return
    await start_cmd_internal_workflow(
        state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, callback=callback
    )
