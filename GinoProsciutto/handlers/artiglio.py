from utils import Utils
from telethon import events, Button


@events.register(events.NewMessage(pattern="/artiglio"))
async def artiglio(event: events.newmessage.NewMessage):
    bot = event.client
    await bot.send_message(
        event.chat,
        message="Spostato al nuovo bot",
    )
