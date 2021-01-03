from enum import Enum


class ArgumentsFillStatus(Enum):
    FILLED = 1
    NOT_FILLED = 2
    FAILED = 3


class CommandFillStatus(Enum):
    FILL_COMMAND = 1
    FILL_ARGUMENTS = 2
