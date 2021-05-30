class BotDBException(Exception):
    """DB exception"""


class AlreadyHasItException(BotDBException):
    """The database already has such a record"""


class NoSuchUser(BotDBException):
    """No such user in database"""


class NoSuchChannel(BotDBException):
    """No such channel in database"""


class ActuatorsRuntimeException(Exception):
    ...


class ActuatorAlreadyConnected(ActuatorsRuntimeException):
    """Actuator already plugged on"""


class NoSuchActuatorInRAM(ActuatorsRuntimeException):
    """No such client in ram_storage"""


class NoSuchCommand(ActuatorsRuntimeException):
    """No such command for client"""

    def __init__(self, cmd: str, *args):
        super().__init__(*args)
        self.cmd = cmd
