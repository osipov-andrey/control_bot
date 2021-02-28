"""
TgAPI --(cmd)--> Handler --(event)--> Observer
"""
from dataclasses import asdict

from core._helpers import MessageTarget, TargetType
from core.bot.constant_strings import COMMAND_IS_NOT_FILLED, CONTEXT_CANCEL_MENU
from core.bot.handlers.actuator_commands.actuator_command import ActuatorCommand
from core.bot.state_enums import ArgumentsFillStatus, CommandFillStatus
from core.bot.states import Command
from core.bot.telegram_api import state_storage
from core.bot.template_strings import COMMAND_IS_NOT_EXIST, NO_SUCH_CLIENT
from core.inbox.messages import message_fabric
from core.memory_storage import NoSuchActuator, NoSuchCommand
from core.sse.sse_event import SSEEvent


async def start_actuator_command_workflow(message, state, mediator, message_id=None):
    command_state = await state.get_state()
    user_id = chat_id = message.chat.id

    message_kwargs = {
        "target": asdict(MessageTarget(TargetType.USER.value, user_id, message_id))
    }

    actuator_name, command, args = ActuatorCommand.parse_cmd_string(message.text)

    if not await mediator.users.has_grant(user_id, actuator_name):
        await message.answer(text="Неизвестная команда или у вас нет доступа к данному актуатору")
        await state.reset_state()
        return

    is_admin = await mediator.users.is_admin(user_id)

    if command is None and command_state is None:
        # Пришло только имя клиента - показываем возможные команды
        try:
            message_kwargs["text"] = get_client_commands(mediator, actuator_name, is_admin)
        except NoSuchActuator:
            message_kwargs["text"] = "Неизвестный актуатор!"
            await state.reset_state()
            return
        finally:
            await mediator.send(message_fabric(message_kwargs))

        await Command.client.set()
        await state_storage.update_data(
            user=user_id,
            chat=chat_id,
            client=actuator_name,
        )
        return
    elif command is None and command_state is not None:
        # Не указана команда
        message_kwargs["text"] = COMMAND_IS_NOT_FILLED + CONTEXT_CANCEL_MENU
        await mediator.send(message_fabric(message_kwargs))
        return

    # Указаны клиент и команда:
    exception = False
    try:
        cmd = ActuatorCommand(actuator_name, command, args, user_id, is_admin)
        if not cmd.cmd_scheme:
            return
        await continue_cmd_workflow(
            state, cmd, message_kwargs, CommandFillStatus.FILL_COMMAND, mediator, message_id
        )
    except NoSuchCommand as e:
        exception = True
        message_kwargs["text"] = COMMAND_IS_NOT_EXIST.format(command=e.cmd)
    except NoSuchActuator:
        exception = True
        message_kwargs["text"] = NO_SUCH_CLIENT.format(client=actuator_name)
    if exception:
        await mediator.send(message_fabric(message_kwargs))
        await state.reset_state()


async def continue_cmd_workflow(
        state, cmd: ActuatorCommand, message_kwargs, fill_status, mediator, message_id=None
):
    cmd_fill_status = cmd.fill_status
    if cmd_fill_status == ArgumentsFillStatus.FILLED:
        # Команда заполнена
        await _finish_cmd_workflow(state, cmd, mediator, message_id)
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
        await mediator.send(message_fabric(message_kwargs))
    # TODO:
    # elif cmd_fill_status == ArgumentsFillStatus.FAILED:
    #     message_kwargs['text'] = cmd.generate_error_report(fill_status)
    #     await telegram_dispatcher.observer.send_message_to_user(**message_kwargs)


async def _finish_cmd_workflow(state, cmd: ActuatorCommand, mediator, message_id=None):
    await state.reset_state()
    event = SSEEvent(
        command=cmd.cmd,
        target=MessageTarget(target_type=TargetType.USER.value, target_name=cmd.user_id, message_id=message_id),
        args=cmd.filled_args,
        behavior=cmd.behavior
    )
    await mediator.actuators.emit_event(cmd.client, event)


def get_client_commands(mediator, client_name: str, is_admin=False) -> str:
    commands = mediator.actuators.get_actuator_info(client_name)
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
