import asyncio
import logging
import json

from aiohttp import web
from aiohttp.web import Application, HTTPBadRequest
from aiohttp_sse import sse_response


log = logging.getLogger(__name__)


async def sse_connect(request):
    client_name = request.match_info.get("client_name")

    bot = request.app["bot"]

    events_queue: asyncio.Queue = bot.add_client(client_name)
    if not events_queue:
        raise HTTPBadRequest()
    log.debug(
        f"{request.remote} has been joined to terminal: {client_name}"
    )
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }

    async with sse_response(request, headers=headers) as response:
        try:
            # introduce:
            await response.send(json.dumps({"client_name": client_name}))
            await response.send(
                json.dumps({"command": "getAvailableMethods", "target":{"target_type": "service", "target_name": client_name}}), event="start"
            )
            while not response.task.done():
                payload = await events_queue.get()
                log.debug(
                    f"{request.remote} sent message with {payload}"
                )
                await response.send(payload, event="slave")
                events_queue.task_done()
        finally:
            bot.remove_client(client_name)
            log.debug(
                f"{request._transport_peername[0]} has been left from terminal: {client_name}"
            )
    return response


def create_sse_server(bot):
    app = Application()
    app["bot"] = bot
    app.router.add_route("GET", "/sse/{client_name}/events", sse_connect)
    asyncio.ensure_future(web._run_app(app, host="localhost", port=8080))
    return app
