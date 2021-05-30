from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._notification_templates import emojies, generate_channel_report
from core.bot.handlers._base_handler import MessageHandler
from core.bot._helpers import get_menu, MenuTextButton
from core.bot.states import MainMenu
from core.bot.telegram_api import telegram_api_dispatcher as d
from core.repository.db_enums import UserEvents
from core.bot._command_constants import ME, INTRODUCE, MY_ID, MY_CHANNELS


@d.class_message_handler(commands=[ME])
class MeHandler(MessageHandler):
    """Private office submenu"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await MainMenu.me.set()
        menu = get_menu(
            header=f"{emojies.ME} Account settings: ",
            commands=[
                MenuTextButton(INTRODUCE, "Write my ID to the bot"),
                MenuTextButton(MY_ID, "My telegram ID"),
                MenuTextButton(MY_CHANNELS, "My channels"),
            ],
        )
        await self._answer(message, menu)


@d.class_message_handler(commands=[INTRODUCE], state=MainMenu.me)
class IntroduceHandler(MessageHandler):
    """Save your data to the bot"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        user_status = await self.mediator.users.upsert(
            tg_id=message.from_user.id,
            tg_username=message.from_user.username,
            name=message.from_user.full_name,
        )
        if user_status == UserEvents.CREATED:
            await self._answer(message, "You have registered")
        elif user_status == UserEvents.UPDATED:
            await self._answer(message, "Your contact information has been updated")

        await state.reset_state()


@d.class_message_handler(commands=[MY_ID], state=MainMenu.me)
class MyIDHandler(MessageHandler):
    """Show my telegram ID"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        user_id = message.from_user.id
        await message.answer(f"Your telegram ID: {user_id}")
        await state.reset_state()


@d.class_message_handler(commands=[MY_CHANNELS], state=MainMenu.me)
class MyChannelsHandler(MessageHandler):
    """Show channels i'm subscribed to"""

    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        channels = await self.mediator.channels.get_subscribes(self.user_telegram_id)
        text = "<b>Channels you subscribed to:</b>\n" + generate_channel_report(channels)
        await self._answer(message, text)
        await state.reset_state()
