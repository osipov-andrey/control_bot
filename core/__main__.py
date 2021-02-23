import argparse
import logging

from core.mediator import Mediator
from core.local_storage.migrations import create_tables

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    bot = Mediator()

    parser = argparse.ArgumentParser(prog="SPYDER", )
    subparsers = parser.add_subparsers(help="Operating mode")
    parser_start = subparsers.add_parser("run", help="Run bot")
    parser_start.set_defaults(func=bot.run)

    parser_db = subparsers.add_parser("db", help="Create database")
    parser_db.set_defaults(func=create_tables)

    args = parser.parse_args()
    args.func()

