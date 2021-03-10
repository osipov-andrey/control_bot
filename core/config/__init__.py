from defaultenv import env


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
