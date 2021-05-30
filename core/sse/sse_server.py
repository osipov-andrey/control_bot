import asyncio
import logging

from aiohttp import web
from aiohttp.web import Application, HTTPBadRequest
from aiohttp.web_exceptions import HTTPTooManyRequests
from aiohttp_sse import sse_response

from core import exceptions
from core.inbox.models import MessageTarget, TargetType
from core._helpers import Behavior
from core.config import config
from .sse_event import SSEEvent

log = logging.getLogger(__name__)
_HOST = config["sse"]["host"]
_PORT = config["sse"]["port"]


def get_intro_event(client_name: str) -> SSEEvent:
    target = MessageTarget(target_type=TargetType.SERVICE.value, target_name=client_name)
    intro_event = SSEEvent(
        event="start",
        command="getAvailableMethods",
        target=target,
        behavior=Behavior.SERVICE.value,
    )
    return intro_event


async def sse_connect(request):
    client_name = request.match_info.get("client_name")

    bot = request.app["bot"]

    try:
        events_queue: asyncio.Queue = await bot.actuators.turn_on_actuator(client_name)
    except exceptions.ActuatorAlreadyConnected:
        raise HTTPTooManyRequests()

    log.info(f"{request.remote} has been joined to terminal: {client_name}")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }

    async with sse_response(request, headers=headers) as response:
        try:
            intro_event = get_intro_event(client_name)
            await response.send(intro_event.data, event=intro_event.event)

            while not response.task.done():
                event = await events_queue.get()
                log.info(f"{request.remote} sent message with {event}")
                await response.send(event.data, event=event.event)
                events_queue.task_done()
        finally:
            await bot.actuators.turn_off_actuator(client_name)
            log.info(f"{request._transport_peername[0]} has been left from terminal: {client_name}")
    return response


def create_sse_server(bot):
    app = Application()
    app["bot"] = bot
    app.router.add_route("GET", "/sse/{client_name}/events", sse_connect)
    asyncio.ensure_future(web._run_app(app, host=_HOST, port=_PORT))
    return app
