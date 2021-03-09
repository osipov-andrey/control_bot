import os


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


