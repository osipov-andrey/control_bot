import os

import yaml


class Config(dict):
    def __init__(
        self, file_config: str = None, dict_config: dict = None, env_prefix: str = None
    ) -> None:
        super().__init__()

        if file_config:
            with open(file_config) as f:
                self.update(**yaml.load(f, Loader=yaml.FullLoader))

        if dict_config:
            self.update(**dict_config)

        if env_prefix:
            for key, value in os.environ.items():
                if key.startswith(env_prefix):
                    self[key] = value

        self._check_config()

    def _check_config(self):
        queue = [("main", self)]
        errors = []

        for prefix, dict_ in queue:  # type: str, dict

            for key, value in dict_.items():
                if isinstance(value, dict):
                    queue.append((self._join_conf(prefix, key), value))
                    continue

                if not value:
                    errors.append(self._join_conf(prefix, key))

                    dict_[key] = value

        if errors:
            raise RuntimeError(f"broken config variables: {errors}")

    @staticmethod
    def _join_conf(*args):
        return " -> ".join(args)
