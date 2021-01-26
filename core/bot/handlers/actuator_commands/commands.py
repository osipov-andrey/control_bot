"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.types import CallbackQuery

from core._helpers import MessageTarget, TargetTypes
from core.bot.constant_strings import COMMAND_IS_NOT_FILLED, CONTEXT_CANCEL_MENU
from core.bot.handlers.actuator_commands._command import TelegramBotCommand
from core.bot.state_enums import ArgumentsFillStatus, CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import state_storage, telegram_api_dispatcher
from core.bot.template_strings import COMMAND_IS_NOT_EXIST, NO_SUCH_CLIENT
from core.inbox.messages import message_fabric
from core.memory_storage import NoSuchActuator, NoSuchCommand
from core.sse.sse_event import SSEEvent


_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


@telegram_api_dispatcher.message_handler(regexp=_COMMAND_REGEX)
async def commands_handler(message: types.Message, state: FSMContext):
    print(message)
    await _start_command_workflow(message, state)


@telegram_api_dispatcher.message_handler(state=Command.arguments)
async def argument_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    message_kwargs = {"target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()}
    data = await state.get_data()
    cmd: TelegramBotCommand = data.get("cmd")

    argument_value = message.text
    cmd.fill_argument(argument_value)

    await continue_cmd_workflow(state, cmd, message_kwargs, CommandFillStatus.FILL_ARGUMENTS)


@telegram_api_dispatcher.message_handler(state=Command.client)
async def client_commands_handler(message: types.Message, state: FSMContext):
    """ Вызов команд из меню клиента """
    await _start_command_workflow(message, state)


@telegram_api_dispatcher.callback_query_handler(lambda callback_query: True, state='*')
async def inline_buttons_handler(callback_query: CallbackQuery, state: FSMContext):
    # Обязательно сразу сделать answer, чтобы убрать "часики" после нажатия на кнопку.
    await callback_query.answer('Button has been Pressed')

    message = callback_query.message
    message.text = callback_query.data

    await _start_command_workflow(message, state, message.message_id)


async def _start_command_workflow(message, state, message_id=None):
    observer = telegram_api_dispatcher.observer
    command_state = await state.get_state()
    user_id = chat_id = message.chat.id

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id, message_id)._asdict()
    }

    actuator_name, command, args = TelegramBotCommand.parse_cmd_string(message.text)

    if not await observer.users.has_grant(user_id, actuator_name):
        await message.answer(text="Неизвестная команда или у вас нет доступа к данному актуатору")
        await state.reset_state()
        return

    is_admin = await observer.users.is_admin(user_id)

    if command is None and command_state is None:
        # Пришло только имя клиента - показываем возможные команды
        try:
            message_kwargs["text"] = get_client_commands(actuator_name, is_admin)
        except NoSuchActuator:
            message_kwargs["text"] = "Неизвестный актуатор!"
            await state.reset_state()
            return
        finally:
            await observer.send(message_fabric(message_kwargs))

        await Command.client.set()
        await state_storage.update_data(
            user=user_id,
            chat=chat_id,
            client=actuator_name,
        )
        # await state.reset_state()
        # await Command.command.set()
        return
    elif command is None and command_state is not None:
        # Не указана команда
        message_kwargs["text"] = COMMAND_IS_NOT_FILLED + CONTEXT_CANCEL_MENU
        await observer.send(message_fabric(message_kwargs))
        return

    # Указаны клиент и команда:
    exception = False
    try:
        cmd = TelegramBotCommand(actuator_name, command, args, user_id, is_admin)
        if not cmd.cmd_scheme:
            return
        await continue_cmd_workflow(
            state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, message_id
        )
    except NoSuchCommand as e:
        exception = True
        message_kwargs["text"] = COMMAND_IS_NOT_EXIST.format(command=e.cmd)
    except NoSuchActuator:
        exception = True
        message_kwargs["text"] = NO_SUCH_CLIENT.format(client=actuator_name)
    if exception:
        await observer.send(message_fabric(message_kwargs))
        await state.reset_state()


async def continue_cmd_workflow(
        state, cmd: TelegramBotCommand, message_kwargs, fill_status, message_id=None
):
    observer = telegram_api_dispatcher.observer
    cmd_fill_status = cmd.fill_status
    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        # Команда заполнена
        await _finish_cmd_workflow(state, cmd, message_id)
    elif cmd_fill_status == ArgumentsFillStatus.NOT_FILLED:
        # Команда не заполнена:

        await state_storage.update_data(
            user=cmd.user_id,
            chat=cmd.user_id,
            cmd=cmd,
        )
        next_step_kwargs = await cmd.get_next_step()
        message_kwargs.update(next_step_kwargs)
        # Arguments input state:
        await Command.arguments.set()
        await observer.send(message_fabric(message_kwargs))
    # TODO:
    # elif cmd_fill_status == ArgumentsFillStatus.FAILED:
    #     message_kwargs['text'] = cmd.generate_error_report(fill_status)
    #     await d.observer.send_message_to_user(**message_kwargs)


async def _finish_cmd_workflow(state, cmd: TelegramBotCommand, message_id=None):
    observer = telegram_api_dispatcher.observer
    await state.reset_state()
    event = SSEEvent(
        command=cmd.cmd,
        target=MessageTarget(target_type="user", target_name=cmd.user_id, message_id=message_id),
        args=cmd.filled_args,
        behavior=cmd.behavior
    )
    await observer.actuators.emit_event(cmd.client, event)


def get_client_commands(client_name: str, is_admin=False) -> str:
    observer = telegram_api_dispatcher.observer
    commands = observer.actuators.get_actuator_info(client_name)
    message = "Информация о командах:\n"
    for cmd in commands.values():
        if cmd.hidden:
            continue
        if cmd.behavior__admin and is_admin:
            message += f"{cmd.behavior__admin.description}\n"
        elif cmd.behavior__user:
            message += f"{cmd.behavior__user.description}\n"
    message += CONTEXT_CANCEL_MENU
    return message
