import logging

from core.mediator import Mediator


logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    bot = Mediator()
    bot.run()
