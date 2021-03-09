from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton
from core.bot.handlers._base_handler import MessageHandler
from core.bot.telegram_api import telegram_api_dispatcher
from core.bot._command_constants import *


@telegram_api_dispatcher.class_message_handler(commands=[START])
class MainMenuHandler(MessageHandler):
    """ Main menu """

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        admins = await self.mediator.users.get_admins()
        if not admins:
            await self._auto_create_admin(message)
            return

        actuators = [
            MenuTextButton(actuator.name, actuator.description)
            for actuator in await self.mediator.actuators.get_all()
            if self.mediator.actuators.is_connected(actuator.name)
            and await self.mediator.users.has_grant(self.user_telegram_id, actuator.name)
        ]
        menu = get_menu(
            header="Main menu:",
            commands=[
                         MenuTextButton(START, "main menu"),
                         MenuTextButton(USERS, "actions with users", admin_only=True),
                         MenuTextButton(CHANNELS, "actions with channels", admin_only=True),
                         MenuTextButton(ACTUATORS, "actions with actuators", admin_only=True),
                         MenuTextButton(ME, "account settings"),
                     ] + actuators,
            is_admin=self.is_admin
        )
        await self._answer(message, menu)

    async def _auto_create_admin(self, message: types.Message):
        await self.mediator.users.upsert(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            name=message.from_user.full_name,
            is_admin=True
        )
        await self._answer(message, "You are now the bot administrator")