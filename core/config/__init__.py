from pathlib import Path

import yaml
from defaultenv import env


__all__ = ['config']


def check_variables(conf: dict, bad_vars: list, parent=""):
    for key, value in conf.items():
        if isinstance(value, dict):
            if parent:
                parent = parent + " - " + key
            check_variables(value, bad_vars, parent=parent)
        if not value:
            if parent:
                bad_vars.append(parent + " - " + key)
            else:
                bad_vars.append(key)


config = dict(
    API_TOKEN=env("API_TOKEN"),
    sse=dict(
        host=env("SSE_HOST"),
        port=env("SSE_PORT")
    ),
    rabbit=dict(
        host=env("RABBIT_HOST"),
        port=env("RABBIT_PORT"),
        login=env("RABBIT_LOGIN"),
        pwd=env("RABBIT_PWD"),
        rabbit_queue=env("RABBIT_QUEUE"),
    )
)

bad_vars = []
check_variables(config, bad_vars)
if bad_vars:
    raise RuntimeError(f"Can't get these variables: {bad_vars}")

with open(Path(__file__).parent.absolute() / "logging.yml") as f:
    logging_config = yaml.load(f, Loader=yaml.SafeLoader)

path_to_configs = Path("logs") / logging_config["handlers"]["file"]["filename"]
logging_config["handlers"]["file"]["filename"] = path_to_configs

config["logging"] = logging_config
