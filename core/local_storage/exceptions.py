class AlreadyHasItException(BaseException):
    """ В БД уже есть такая запись """


class NoSuchUser(BaseException):
    """ Нет такого пользователя в БД """
