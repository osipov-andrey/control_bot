from core.bot import emojies

COMMAND_IS_NOT_EXIST = ' Команды: "{command}" не существует.'
NO_SUCH_CLIENT = ' Нет подключения к клиенту "{client}"'


def generate_channel_report(channels):
    text = "\n".join(f"{emojies.CHANNEL}<b>{c.name}</b> - {c.description}" for c in channels)
    if not text:
        text = "No channels!"
    return text
