from typing import List

from core.inbox.models import ArgInfo
from core.repository import User, Actuator
from core.mediator.dependency import MediatorDependency


async def generate_prompt(argument_info: ArgInfo, filled_args: dict) -> str:
    """ Generate prompt for the current argument during command invocation """
    prompt = ""
    if argument_info.is_user:
        prompt = await _get_users_prompt()
    elif argument_info.is_actuator:
        prompt = await _get_actuators_prompt()
    elif argument_info.is_channel:
        prompt = await _get_channels_prompt()
    elif argument_info.is_granter:
        # Чтобы получить подсказку по пользователям, имеющим доступ к актуатору,
        # надо сначала указать сам актуатор (при вызове команды)
        actuator_name = filled_args.get("actuator")
        if actuator_name is not None:
            prompt = await _get_granters_prompt(actuator_name)
    elif argument_info.is_subscriber:
        # Like is_granter
        channel = filled_args.get("channel")
        if channel is not None:
            prompt = await _get_subscribers_prompt(channel)
    if prompt:
        prompt = "\nℹ️" + prompt
    return prompt


async def _get_granters_prompt(actuator_name: str) -> str:
    prompt = f"<b>Users with {actuator_name} grant:</b>\n"
    granters: List[User] = await MediatorDependency.mediator.actuators.get_granters(
        actuator_name
    )
    if granters:
        prompt += "".join(
            f"/{granter.telegram_id} - {granter.name}\n" for granter in granters
        )
    else:
        prompt += "No users"
    return prompt


async def _get_actuators_prompt():
    prompt = "<b>Registered actuators:</b>\n"
    actuators: List[Actuator] = await MediatorDependency.mediator.actuators.get_all()
    if actuators:
        prompt += "".join(
            f"/{actuator.name} - {actuator.description}\n" for actuator in actuators
        )
    else:
        prompt += "No registered actuators"
    return prompt


async def _get_users_prompt() -> str:
    prompt = "<b>Registered users:</b>\n"
    users: List[User] = await MediatorDependency.mediator.users.get_all()
    if users:
        prompt += "".join(f"/{user.telegram_id} - {user.name}\n" for user in users)
    else:
        prompt += "No registered users"
    return prompt


async def _get_subscribers_prompt(channel: str) -> str:
    """ Take prompt about channel subscribers """
    subscribers = await MediatorDependency.mediator.channels.get_subscribers(channel)
    prompt = f"<b>{channel} subscribers:</b>\n"
    if subscribers:
        prompt += "".join(f"/{s.telegram_id} - {s.name}\n" for s in subscribers)
    else:
        prompt += "No subscribers"
    return prompt


async def _get_channels_prompt():
    """ Take prompt about channels """
    channels = await MediatorDependency.mediator.channels.all_channels()
    prompt = "<b>Registered channels:</b>\n"
    if channels:
        prompt += "".join(
            f"/{channel.name} - {channel.description}\n" for channel in channels
        )
    else:
        prompt += "No channels"
    return prompt
