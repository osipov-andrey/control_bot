from typing import Dict, Optional

from core.inbox.models import Issue, CommandSchema
from core.exceptions import NoSuchActuatorInRAM, NoSuchCommand


class ControlBotMemoryStorage:
    """Stores in RAM information about connected actuators, issues, etc."""

    def __init__(self):
        self._storage = dict()
        self._issue_storage: Dict[str, Issue] = dict()

    def save_actuator_info(self, actuator_name: str, commands_info: dict):
        self._storage[actuator_name] = commands_info

    def remove_actuator(self, actuator_name: str):
        self._storage.pop(actuator_name)

    def get_actuator_info(self, actuator_name: str):
        try:
            return self._storage[actuator_name]
        except KeyError:
            raise NoSuchActuatorInRAM(actuator_name)

    def get_command_info(self, actuator_name: str, command: str):
        try:
            return self.get_actuator_info(actuator_name)[command]
        except KeyError:
            raise NoSuchCommand(actuator_name, command)

    def set_issue(self, issue: Issue):
        self._issue_storage[issue.issue_id] = issue

    def resolve_issue(self, issue_id: str) -> Optional[Issue]:
        issue: Optional[Issue] = self._issue_storage.get(issue_id)
        return issue
