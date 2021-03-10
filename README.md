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
2. Создаем файл *.env* и заполняем (рядом и по образцу с *.env.template*).
3. Запускаем:
> pip install -r requirements.txt 
>
> python -m core db
> 
> python -m core run

5. Заходим в вашего бота в телеграме, жмем `\start`.
   Должно прийти сообщение, что вы теперь админ бота.
   После этого вызываем главное меню через ту же команду.
   Подключаемые актуаторы будут появляться в главном меню.

SSE-сервер будет работать по адресу:
http://localhost:8080/sse/ACTUATOR_NAME/events,
где HOST, PORT - из конфига, ACTUATOR_NAME - имя подключаемого актуатора.

## Docker (in work)

1. docker-compose build
2. docker-compose run app db
3. docker-compose up -d
