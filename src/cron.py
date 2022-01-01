from telethon import TelegramClient
from utils import Utils
import asyncio
import re


async def journal_log():
    bot = TelegramClient("cron", api_id=Utils.APP_ID, api_hash=Utils.APP_HASH)
    await bot.start(bot_token=Utils.TOKEN)
    await bot.connect()
    gino = await bot.get_entity("https://t.me/ilginop")
    cmd = Utils.status_commands[2].get("🌡️ temp")
    temp = await Utils._exec(gino.id, cmd=cmd, name="🌡️ temp")
    temp = Utils.get_temperature(temp)
    temp = re.search(r"[0-9]+\.[0-9]+", temp).group(0)
    if float(temp) >= 50.00:
        await bot.send_message(gino, f"CPU TEMPERATURE WARNING: {temp}°C")


asyncio.run(journal_log())
