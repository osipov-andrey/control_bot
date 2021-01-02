import asyncio
import logging

from aiohttp import web
from aiohttp.web import Application, HTTPBadRequest
from aiohttp_sse import sse_response

from core._helpers import MessageTarget
from core.config import config
from core.sse.sse_event import SSEEvent

log = logging.getLogger(__name__)
_HOST = config["sse"]["host"]
_PORT = config["sse"]["port"]


def get_intro_event(client_name: str) -> SSEEvent:
    target = MessageTarget("service", client_name)
    intro_event = SSEEvent(event="start", command="getAvailableMethods", target=target)
    return intro_event


async def sse_connect(request):
    client_name = request.match_info.get("client_name")

    bot = request.app["bot"]

    events_queue: asyncio.Queue = bot.new_sse_connection(client_name)
    if not events_queue:
        raise HTTPBadRequest()
    log.info(
        f"{request.remote} has been joined to terminal: {client_name}"
    )
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }

    async with sse_response(request, headers=headers) as response:
        try:
            intro_event = get_intro_event(client_name)
            await response.send(intro_event.data, event=intro_event.event)

            while not response.task.done():
                payload = await events_queue.get()
                log.info(
                    f"{request.remote} sent message with {payload}"
                )
                await response.send(payload)
                events_queue.task_done()
        finally:
            bot.stop_sse_connection(client_name)
            log.info(
                f"{request._transport_peername[0]} has been left from terminal: {client_name}"
            )
    return response


def create_sse_server(bot):
    app = Application()
    app["bot"] = bot
    app.router.add_route("GET", "/sse/{client_name}/events", sse_connect)
    asyncio.ensure_future(web._run_app(app, host=_HOST, port=_PORT))
    return app
