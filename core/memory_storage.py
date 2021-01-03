from core._helpers import ClientCommandInfo


class NoSuchClient(Exception):
    """ No such client """


class NoSuchCommand(Exception):
    """ No such command for client"""


class MemoryStorage:

    def __init__(self):
        self._storage = dict()

    def save_client(self, client_name: str, commands_info: dict):
        # TODO: schema validation

        commands_info = {
            cmd: ClientCommandInfo(**info)
            for cmd, info in commands_info.items()
        }
        self._storage[client_name] = commands_info

    def remove_client(self, client_name: str):
        self._storage.pop(client_name)

    def get_client_info(self, client_name: str):
        try:
            return self._storage[client_name]
        except KeyError:
            raise NoSuchClient(client_name)

    def get_command_info(self, client_name: str, command: str):
        try:
            return self.get_client_info(client_name)[command]
        except KeyError:
            raise NoSuchCommand(client_name, command)
