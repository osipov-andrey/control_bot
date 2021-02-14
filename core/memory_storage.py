from ._helpers import CommandSchema, Issue


class NoSuchActuator(Exception):
    """ No such client """


class NoSuchCommand(Exception):
    """ No such command for client"""
    def __init__(self, cmd: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd = cmd


class ControlBotMemoryStorage:
    """ Хранит информацию о командах подключенных клиентов, об issues и т.п..."""
    def __init__(self):
        self._storage = dict()
        self._issue_storage = dict()

    def save_client(self, client_name: str, commands_info: dict):
        # TODO: schema validation

        commands_info = {
            cmd: CommandSchema(**info)
            for cmd, info in commands_info.items()
        }
        self._storage[client_name] = commands_info

    def remove_client(self, client_name: str):
        self._storage.pop(client_name)

    def get_client_info(self, client_name: str):
        try:
            return self._storage[client_name]
        except KeyError:
            raise NoSuchActuator(client_name)

    def get_command_info(self, client_name: str, command: str):
        try:
            return self.get_client_info(client_name)[command]
        except KeyError:
            raise NoSuchCommand(client_name, command)

    def set_issue(self, issue: Issue):
        self._issue_storage[issue.issue_id] = issue

    def resolve_issue(self, issue_id: str) -> Issue:
        issue = self._issue_storage.get(issue_id)
        return issue
