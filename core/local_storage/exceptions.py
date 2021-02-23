class BotDBException(Exception):
    """ DB exception """


class AlreadyHasItException(BotDBException):
    """ В БД уже есть такая запись """


class NoSuchUser(BotDBException):
    """ Нет такого пользователя в БД """


class NoSuchChannel(BotDBException):
    """ No such channel in database """
