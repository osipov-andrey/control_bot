class BotDBException(Exception):
    """ DB exception """


class AlreadyHasItException(BotDBException):
    """ The database already has such a record """


class NoSuchUser(BotDBException):
    """ No such user in database """


class NoSuchChannel(BotDBException):
    """ No such channel in database """


class ActuatorAlreadyConnected(Exception):
    """ Actuator already plugged on """
