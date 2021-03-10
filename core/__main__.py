import argparse
import logging


logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    from mediator import mediator

    parser = argparse.ArgumentParser(prog="Bot", )
    subparsers = parser.add_subparsers(help="Operating mode")
    parser_start = subparsers.add_parser("run", help="Run bot")
    parser_start.set_defaults(func=mediator.run)

    args = parser.parse_args()
    args.func()
