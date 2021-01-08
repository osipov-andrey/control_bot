"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.types import CallbackQuery

from core._helpers import MessageTarget, TargetTypes
from core.bot.constant_strings import COMMAND_IS_NOT_FILLED, CONTEXT_CANCEL_MENU
from core.bot.handlers._command import TelegramBotCommand
from core.bot.state_enums import ArgumentsFillStatus, CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import state_storage, telegram_api_dispatcher as d
from core.bot.template_strings import COMMAND_IS_NOT_EXIST, NO_SUCH_CLIENT
from core.inbox.messages import message_fabric
from core.memory_storage import NoSuchClient, NoSuchCommand
from core.sse.sse_event import SSEEvent

_COMMAND_REGEX = r"^\/([^_]*)_?.*?$"


@d.message_handler(regexp=_COMMAND_REGEX)
async def commands_handler(message: types.Message, state: FSMContext):
    print(message)
    await _start_command_workflow(message, state)


@d.message_handler(state=Command.arguments)
async def argument_handler(message: types.Message, state: FSMContext):
    user_id = chat_id = message.chat.id
    message_kwargs = {"target": MessageTarget(TargetTypes.USER.value, user_id)._asdict()}
    data = await state.get_data()
    cmd: TelegramBotCommand = data.get("cmd")

    argument_value = message.text
    cmd.fill_argument(argument_value)

    await _continue_cmd_workflow(state, cmd, message_kwargs, CommandFillStatus.FILL_ARGUMENTS)


@d.message_handler(state=Command.client)
async def client_commands_handler(message: types.Message, state: FSMContext):
    """ Вызов команд из меню клиента """
    await _start_command_workflow(message, state)


@d.callback_query_handler(lambda callback_query: True, state='*')
async def inline_buttons_handler(callback_query: CallbackQuery, state: FSMContext):
    # Обязательно сразу сделать answer, чтобы убрать "часики" после нажатия на кнопку.
    await callback_query.answer('Button has been Pressed')

    message = callback_query.message
    message.text = callback_query.data

    await _start_command_workflow(message, state, message.message_id)


async def _start_command_workflow(message, state, message_id=None):
    command_state = await state.get_state()
    user_id = chat_id = message.chat.id

    message_kwargs = {
        "target": MessageTarget(TargetTypes.USER.value, user_id, message_id)._asdict()
    }

    client, command, args = TelegramBotCommand.parse_cmd_string(message.text)

    # TODO проверка прав пользователя на клиента
    # if not db.grants.has_access(client_name, user_id):
    #     return
    # TODO is_admin?
    # is_admin = db.superuser.is_admin(user_id)
    is_admin = False

    if command is None and command_state is None:
        # Пришло только имя клиента - показываем возможные команды
        #TODO если нет клиента:
        message_kwargs["text"] = get_client_commands(client, is_admin)

        await d.observer.send(message_fabric(message_kwargs))

        await Command.client.set()
        await state_storage.update_data(
            user=user_id,
            chat=chat_id,
            client=client,
        )
        # await state.reset_state()
        # await Command.command.set()
        return
    elif command is None and command_state is not None:
        # Не указана команда
        message_kwargs["text"] = COMMAND_IS_NOT_FILLED + CONTEXT_CANCEL_MENU
        await d.observer.send(message_fabric(message_kwargs))
        return

    # Указаны клиент и команда:
    exception = False
    try:
        cmd = TelegramBotCommand(client, command, args, user_id)
        await _continue_cmd_workflow(
            state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, message_id
        )
    except NoSuchCommand as e:
        exception = True
        message_kwargs["text"] = COMMAND_IS_NOT_EXIST.format(command=e.cmd)
    except NoSuchClient:
        exception = True
        message_kwargs["text"] = NO_SUCH_CLIENT.format(client=client)
    if exception:
        await d.observer.send(message_fabric(message_kwargs))
        await state.reset_state()


async def _continue_cmd_workflow(
        state, cmd: TelegramBotCommand, message_kwargs, fill_status, message_id=None
):
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

        message_kwargs.update(cmd.get_next_step())
        # Arguments input state:
        await Command.arguments.set()
        await d.observer.send(message_fabric(message_kwargs))
    # TODO:
    # elif cmd_fill_status == ArgumentsFillStatus.FAILED:
    #     message_kwargs['text'] = cmd.generate_error_report(fill_status)
    #     await d.observer.send_message_to_user(**message_kwargs)


async def _finish_cmd_workflow(state, cmd: TelegramBotCommand, message_id=None):
    await state.reset_state()
    event = SSEEvent(
        command=cmd.cmd,
        target=MessageTarget(target_type="user", target_name=cmd.user_id, message_id=message_id),
        args=cmd.filled_args
    )
    await d.observer.emit_event(cmd.client, event)


def get_client_commands(client_name: str, is_admin=False) -> str:
    commands = d.observer.get_client_info(client_name)
    message = "Информация о командах:\n"
    for cmd in commands.values():
        if not cmd.hidden:
            if (is_admin and cmd.admin_only) or not cmd.admin_only:
                message += f"{cmd.description}\n"
    message += "\n/cancel - Выход в главное меню\n"
    return message
