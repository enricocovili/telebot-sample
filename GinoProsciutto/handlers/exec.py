from utils import Utils
from telethon import events
import logging


@events.register(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    msg = event.text.split()[1:]
    logging.info("received: exec " + " ".join(msg))
    out = await Utils._exec(event.chat_id, cmd=msg)
    await event.reply(out[:4000])
