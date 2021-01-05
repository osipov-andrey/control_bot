import json
from core._helpers import MessageTarget


class SSEEvent:

    def __init__(
            self,
            *,
            event: str = "slave",
            command: str,
            target: MessageTarget,
            args: dict = None
    ):
        self.event = event
        self.command = command
        self.target = target._asdict()
        self.args = args if args else {}

    @property
    def data(self):
        return json.dumps(
            {
                "command": self.command,
                "target": self.target,
                "args": self.args,
            }
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"event='{self.event}', command='{self.command}', " \
               f"target={self.target}), args={self.args}" \
               f")"
