from utils import Utils
import subprocess
from telethon import events


@events.register(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    msg = event.text.split()[1:]
    out = await Utils._exec(event, cmd=msg)
    await event.reply(out[:4000])
