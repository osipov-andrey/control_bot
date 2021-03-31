# Control bot

Телеграм бот для мониторинга и контроля любых внешних систем.

Сам бот не имеет никакой бизнес-логики, за исключением разграничения прав доступа.
Бизнес логика подключается через специальные модули-актуаторы.

Для написания модулей используйте библиотеку [control_bot_actuator (cba)](https://github.com/osipov-andrey/control_bot_actuator).

Между ботом и модулями происходит двухсторонний обмен информацией.

![Alt-текст](https://github.com/osipov-andrey/control_bot/blob/master/docs/main_schema.png?raw=true "Control bot + actuators")

Актуаторы получают команды от бота через SSE. 
Возвращают сообщения с помощью RabbitMQ либо на POST-ручку бота. 

## Запуск

1. Идем в телеграм в `@BotFather`, создаем бот, получаем HTTP API токен.
2. Копируем **.env.template** -> **.env**
3. В  **.env** указываем HTTP API токен, параметры для подключения к кролику, хост и порт для SSE сервера.
4. Запускаем:
> pip install .
>
> pip install -e.[dev] && pre-commit install  # Для разработки
>
> cd core/repository && alembic upgrade head && cd ../..
>  
> python -m core run

5. Заходим в вашего бота в телеграме, жмем `\start`.
   Должно прийти сообщение, что вы теперь админ бота.

6. После этого вызываем главное меню через ту же команду.
   Регистрируем первый актуатор:
   `\start` -> `\actuators` -> `\createActuator`

7. Предоставляем пользователю доступ к актуатору:
   `\start` -> `\users` или `\actuators` -> `\grant`

8. Подключаемые актуаторы под зарегистрированными именами будут появляться в главном меню (для пользователей с доступом).

SSE-сервер будет работать по адресу:
http://localhost:8080/sse/ACTUATOR_NAME/events,
где HOST, PORT - из конфига, ACTUATOR_NAME - имя подключаемого актуатора.

## Docker

1. Заполняем файл .env (см. выше)
2. docker-compose build
3. docker-compose up -d
