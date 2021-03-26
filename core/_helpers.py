from enum import Enum


class ArgType(Enum):
    STR = "string"
    INT = "integer"
    LIST = "list"
    # USER = "user"


class Behavior(Enum):
    USER = "user"
    ADMIN = "admin"
    SERVICE = "service"


def get_log_cover(cover_name: str) -> str:
    cover = (
        f"\n{'#'*20} {cover_name} {'#'*20}"
        f"\n%s"
        f"\n{'#'*20} {' '*len(cover_name)} {'#'*20}"
    )
    return cover
