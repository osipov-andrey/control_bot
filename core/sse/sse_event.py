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
    def compiled(self):
        return json.dumps(
            {
                "event": self.event,
                "data": {key: value for key, value in self.__dict__.items() if key != "event"}
            }
        )
