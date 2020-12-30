from collections import namedtuple


MessageTarget = namedtuple(
    "MessageTarget",
    "target_type, target_name, message_id", defaults=(None, )
)
