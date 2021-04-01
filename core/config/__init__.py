from pathlib import Path

import yaml
from defaultenv import env

from ._config import Config


__all__ = ["config"]


config_dict = dict(
    API_TOKEN=env("API_TOKEN"),
    sse=dict(host=env("SSE_HOST"), port=env("SSE_PORT")),
    rabbit=dict(
        host=env("RABBIT_HOST"),
        port=env("RABBIT_PORT"),
        login=env("RABBIT_LOGIN"),
        pwd=env("RABBIT_PWD"),
        rabbit_queue=env("RABBIT_QUEUE"),
    ),
)

config = Config(dict_config=config_dict)

with open(Path(__file__).parent.absolute() / "logging.yml") as f:
    logging_config = yaml.load(f, Loader=yaml.SafeLoader)

path_to_configs = Path("logs") / logging_config["handlers"]["file"]["filename"]
logging_config["handlers"]["file"]["filename"] = path_to_configs

config["logging"] = logging_config
