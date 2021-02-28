from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from core.bot.handlers._base_handler import MessageHandler
from core.bot.handlers.actuator_commands.actuator_command import ActuatorCommand
from core.bot.handlers.actuator_commands.actuator_commands_workflow import start_actuator_command_workflow, \
    continue_cmd_workflow
from core.bot.state_enums import CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import telegram_api_dispatcher as d


_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


@d.class_message_handler(regexp=_COMMAND_REGEX)
class ActuatorCommandHandler(MessageHandler):
    """ Handle actuator command """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await start_actuator_command_workflow(message, state, self.mediator)


@d.class_message_handler(state=Command.client)
class ActuatorMenuCommandHandler(MessageHandler):
    """ Handle actuator command called from the actuator menu """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await start_actuator_command_workflow(message, state, self.mediator)


@d.class_message_handler(state=Command.arguments)
class FillingArgumentHandler(MessageHandler):
    """ Fill in the argument of the actuator command """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        cmd: ActuatorCommand = data.get("cmd")
        argument_value = message.text
        cmd.fill_argument(argument_value)
        await continue_cmd_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_ARGUMENTS, self.mediator
        )


@d.callback_query_handler(lambda callback_query: True, state='*')
async def inline_buttons_handler(callback_query: CallbackQuery, state: FSMContext):
    from mediator import mediator
    # Обязательно сразу сделать answer, чтобы убрать "часики" после нажатия на кнопку.
    await callback_query.answer('Button has been Pressed')

    message = callback_query.message
    message.text = callback_query.data

    await start_actuator_command_workflow(message, state, mediator, message.message_id)
