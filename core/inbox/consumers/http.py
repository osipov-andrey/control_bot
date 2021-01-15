import json
from aiohttp import web

from core.inbox.messages import message_fabric


async def consume_message(request):
    bot = request.app["bot"]
    content = await request.content.read()
    body = content.decode()
    body = json.loads(body)
    message = message_fabric(body['payload'])
    await bot.inbox_dispatcher.queue.put(message)
    return web.Response()
