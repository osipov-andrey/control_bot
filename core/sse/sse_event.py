import json
from dataclasses import asdict

from core.inbox.models import MessageTarget


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
        self.target = target
        self.args = args if args else {}
        self.behavior = behavior

    @property
    def data(self):
        json_ = json.dumps(
            {
                "command": self.command,
                "target": self.target.dict(),
                "args": self.args,
                "behavior": self.behavior,
            }
        )
        return json_

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"event='{self.event}', command='{self.command}', " \
               f"target={self.target}, behavior='{self.behavior}', args={self.args}" \
               f")"
