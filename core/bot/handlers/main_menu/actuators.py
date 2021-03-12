from aiogram import types
from aiogram.dispatcher import FSMContext

from core.bot._helpers import get_menu, MenuTextButton, admin_only_method
from core.bot import emojies
from core.bot.handlers._base_handler import MessageHandler
from core.bot._command_constants import *
from core.bot.commands.internal.internal_commands_schemas import get_create_or_delete_cmd
from core.bot.commands.internal.internal_commands_workflow import start_cmd_internal_workflow
from core.bot.states import MainMenu
from core.bot.state_enums import CommandFillStatus
from core.bot.telegram_api import telegram_api_dispatcher as d


@d.class_message_handler(commands=[ACTUATORS])
class ActuatorsHandler(MessageHandler):
    """ Actuators submenu """
    @admin_only_method
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        await MainMenu.actuators.set()
        menu = get_menu(
            header=f"{emojies.ACTUATOR} Actuators menu: ",
            commands=[
                MenuTextButton(ALL_ACTUATORS, "Show all registered actuators"),
                MenuTextButton(CREATE_ACTUATOR, "Create actuator"),
                MenuTextButton(DELETE_ACTUATOR, "Delete actuator"),
                MenuTextButton(GRANT, "Grant user to actuator"),
                MenuTextButton(REVOKE, "Revoke user from actuator"),
                # grant, revoke - calling from users submenu
            ]
        )
        await self._answer(message, menu)


@d.class_message_handler(commands=[ALL_ACTUATORS], state=MainMenu.actuators)
class AllActuatorsHandler(MessageHandler):
    """ Show all actuators """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        actuators = await self.mediator.actuators.get_all()
        text = f"{emojies.ACTUATOR} Registered actuators: \n\n"
        text += "\n".join(
            "{connected}{name} - {description}".format(
                connected=emojies.ACTUATOR_CONNECTED if self.mediator.actuators.is_connected(a.name) else '',
                name=f"{emojies.ACTUATOR}<b>{a.name}</b>",
                description=a.description
            ) for a in actuators
        )
        await self._answer(message, text)
        await state.reset_state()


@d.class_message_handler(commands=[CREATE_ACTUATOR], state=MainMenu.actuators)
class CreateActuatorHandler(MessageHandler):
    """ Create actuator """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = get_create_or_delete_cmd(CREATE_ACTUATOR, self.user_telegram_id, self.is_admin)

        async def create_callback(**kwargs_):
            actuator_name = kwargs_.get("actuator")
            description = kwargs_.get("description")
            await self.mediator.actuators.create_actuator(actuator_name, description)
            await self._answer(message, f"Mediator created : {actuator_name} - {description}.")

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=create_callback
        )


@d.class_message_handler(commands=[DELETE_ACTUATOR], state=MainMenu.actuators)
class DeleteActuatorHandler(MessageHandler):
    """ Delete actuator """
    async def handle(self, message: types.Message, state: FSMContext, **kwargs):
        cmd = get_create_or_delete_cmd(DELETE_ACTUATOR, self.user_telegram_id, self.is_admin)

        async def delete_callback(**kwargs_):
            actuator_name = kwargs_.get("actuator")
            await self.mediator.actuators.delete_actuator(actuator_name)
            await self._answer(message, f"Mediator deleted {actuator_name}.")

        await start_cmd_internal_workflow(
            state, cmd, self.kwargs_to_answer, CommandFillStatus.FILL_COMMAND, callback=delete_callback
        )
