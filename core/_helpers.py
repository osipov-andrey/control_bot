from collections import namedtuple
from enum import Enum


class TargetTypes(Enum):
    SERVICE = "service"
    USER = "user"
    CHANNEL = "channel"


# TODO: replace with dataclass?
MessageTarget = namedtuple(
    "MessageTarget",
    "target_type, target_name, message_id", defaults=(None, )
)


CommandScheme = namedtuple(
    "CommandScheme",
    "description, hidden, admin_only, args"
)


def get_log_cover(cover_name: str) -> str:
    cover = f"\n{'#'*20} {cover_name} {'#'*20}" \
            f"\n%s" \
            f"\n{'#'*20} {' '*len(cover_name)} {'#'*20}"
    return cover
