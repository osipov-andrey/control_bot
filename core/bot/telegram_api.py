import aiogram

from core.config import config


__all__ = ['telegram_api_dispatcher']

_API_TOKEN = config["API_TOKEN"]

_bot = aiogram.Bot(token=_API_TOKEN)

telegram_api_dispatcher = aiogram.Dispatcher(bot=_bot)
