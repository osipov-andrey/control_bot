""" Users submenu handlers """

from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import admin_only_method, get_menu, MenuTextButton
from core.bot.handlers._static_commands import *
from core.bot.handlers.main_menu.users_commands import get_grant_or_revoke_cmd, get_subscribe_or_unsubscribe_cmd
from core.bot.handlers.main_menu._workflow import start_cmd_internal_workflow
from core.bot.handlers._base_handler import MessageHandler
from core.repository.exceptions import AlreadyHasItException, NoSuchUser
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d


@d.class_message_handler(commands=[USERS])
class UsersHandler(MessageHandler):
    """ Users submenu """

    @admin_only_method
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
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
    """ Show all users of bot """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        users = await self.mediator.users.get_all()
        text = "\n".join(
            f"👨🏼‍💻{u.name} - {u.telegram_username} - {u.telegram_id} {'<b>🗿(admin)</b>' if u.is_admin else ''}"
            for u in users
        )
        await message.answer(text, parse_mode="HTML")
        await state.reset_state()


@d.class_message_handler(commands=[SUBSCRIBE], state=[MainMenu.users, MainMenu.channels])
class SubscribeHandler(MessageHandler):
    """ Subscribe user to channel """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_subscribe_or_unsubscribe_cmd(SUBSCRIBE, self.user_telegram_id, self.is_admin)

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
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=subscribe_callback
        )


@d.class_message_handler(commands=[UNSUBSCRIBE], state=[MainMenu.users, MainMenu.channels])
class UnsubscribeHandler(MessageHandler):
    """ Unsubscribe user from channel """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_subscribe_or_unsubscribe_cmd(UNSUBSCRIBE, self.user_telegram_id, self.is_admin)

        async def unsubscribe_callback(**kwargs_):
            user_to_subs_id = kwargs_.get("user_id")
            channel = kwargs_.get("channel")
            await self.mediator.channels.unsubscribe(user_to_subs_id, channel)
            await message.answer(f"The user {user_to_subs_id} unsubscribed from channel {channel}")

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=unsubscribe_callback
        )


@d.class_message_handler(commands=[GRANT], state=[MainMenu.users, MainMenu.actuators])
class GrantHandler(MessageHandler):
    """ Grant the user rights to the actuator """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_grant_or_revoke_cmd(GRANT, self.user_telegram_id, self.is_admin)

        async def grant_callback(**kwargs_):
            user_to_grant_id = kwargs_.get("user_id")
            actuator = kwargs_.get("actuator")
            try:
                await self.mediator.actuators.grant(user_to_grant_id, actuator)
                answer = f"User {user_to_grant_id} gained grant to {actuator}"
            except AlreadyHasItException:
                answer = f"User {user_to_grant_id} ALREADY has grant to {actuator}"
            except NoSuchUser:
                answer = "No such user!"
            await message.answer(answer)

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=grant_callback
        )


@d.class_message_handler(commands=[REVOKE], state=[MainMenu.users, MainMenu.actuators])
class RevokeHandler(MessageHandler):
    """ Revoke the user rights to the actuator """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = await get_grant_or_revoke_cmd(REVOKE, self.user_telegram_id, self.is_admin)

        async def revoke_callback(**kwargs_):
            user_to_revoke_id = kwargs_.get("user_id")
            actuator = kwargs_.get("actuator")
            await self.mediator.actuators.revoke(user_to_revoke_id, actuator)
            await message.answer(f"User {user_to_revoke_id} revoke from {actuator}")

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=revoke_callback
        )
