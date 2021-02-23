import json
from dataclasses import asdict

from .._helpers import MessageTarget


class SSEEvent:

    def __init__(
            self,
            *,
            event: str = "slave",
            command: str,
            target: MessageTarget,
            args: dict = None,
            behavior: str
    ):
        self.event = event
        self.command = command
        self.target = asdict(target)
        self.args = args if args else {}
        self.behavior = behavior

    @property
    def data(self):
        return json.dumps(
            {
                "command": self.command,
                "target": self.target,
                "args": self.args,
                "behavior": self.behavior,
            }
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"event='{self.event}', command='{self.command}', " \
               f"target={self.target}, behavior='{self.behavior}', args={self.args}" \
               f")"
