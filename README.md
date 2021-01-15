# Control bot

Телеграм бот для мониторинга и контроля любых внешних систем.

Сам бот не имеет никакой бизнес-логики, за исключением разграничения прав доступа.
Бизнес логика подключается через специальный модули-актуаторы.

Для написания модулей используйте библиотеку [control_bot_actuator (cba)](https://github.com/osipov-andrey/control_bot_actuator).

Между ботом и модулями происходит двухсторонний обмен информацией.

![Alt-текст](https://github.com/osipov-andrey/control_bot/blob/master/docs/main_schema.png?raw=true "Control bot + actuators")

Актуаторы получают команды от бота через SSE. 
Возвращают сообщения с помощью RabbitMQ либо на POST-ручку бота. 