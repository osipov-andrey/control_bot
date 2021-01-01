import logging

from core.observer import Observer


logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    bot = Observer()
    bot.run()
