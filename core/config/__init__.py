import os
# import pathlib
# import yaml


# root = pathlib.Path(__file__).parent.absolute()
# with open(root.joinpath("config.yaml"), "r") as f:
#     config = yaml.load(f, Loader=yaml.SafeLoader)


config = dict(
            API_TOKEN=os.getenv("API_TOKEN"),
            sse=dict(
                host=os.getenv("SSE_HOST"),
                port=os.getenv("SSE_PORT")
            ),
            rabbit=dict(
                    host=os.getenv("RABBIT_HOST"),
                    port=os.getenv("RABBIT_PORT"),
                    login=os.getenv("RABBIT_LOGIN"),
                    pwd=os.getenv("RABBIT_PWD"),
                    rabbit_queue=os.getenv("RABBIT_QUEUE"),
                )
        )


