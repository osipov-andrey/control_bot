# Control bot

Telegram bot for monitoring and managing any external systems.

The bot itself has no business logic, except for the differentiation of access rights.
Business logic is connected through special actuator modules.

Use the library to write modules: [control_bot_actuator (cba)](https://github.com/osipov-andrey/control_bot_actuator).

There is a two-way exchange of information between the bot and the modules.

![Alt-текст](https://github.com/osipov-andrey/control_bot/blob/master/docs/main_schema.png?raw=true "Control bot + actuators")

The actuators receive commands from the bot via SSE and return messages using RabbitMQ.

## Starting

1. Go to the telegram account `@BotFather`, create a bot, get the HTTP API token.
2. Copy **.env.template** -> **.env**
3. In the **.env** file, specify the HTTP API token, parameters for connecting to the rabbit, host and port for the SSE server.
4. Launch:
> pip install .
>
> pip install -e.[dev] && pre-commit install  _(For developing)_
>
> cd core/repository && alembic upgrade head && cd ../..
>  
> python -m core run

5. Go to your bot in telegram, click `\start`. 
   You should receive a message that you are now the admin of the bot.

6. After that, we call the main menu through the same command. 
   Register first actuator:
   `\start` -> `\actuators` -> `\createActuator`

7. Grant the user access to the actuator:
   `\start` -> `\users` или `\actuators` -> `\grant`

8. The connected actuators under the registered names will appear in the main menu (for users with grant).

SSE server will run at:
`http://HOST:PORT/sse/ACTUATOR_NAME/events`,
where HOST, PORT - from the config, ACTUATOR_NAME - the name of the connected actuator.

## Docker

1. Complete the **.env** file (see above)
2. docker-compose build
3. docker-compose up -d


## How it works with Zabbix:

### TODO: add link to zabbix-actuator

![Alt-текст](https://github.com/osipov-andrey/control_bot/blob/eng/docs/zactuator.gif?raw=true "Control bot + Zabbix")