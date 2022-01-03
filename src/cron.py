from telethon import TelegramClient
from telethon.errors import FloodWaitError
from utils import Utils
import asyncio
import re


async def journal_log():
    bot = TelegramClient("cron", api_id=Utils.APP_ID, api_hash=Utils.APP_HASH)
    await bot.start(bot_token=Utils.TOKEN)
    await bot.connect()
    gino_id = Utils.WHITELIST_IDS[0]
    try:
        # using ID instead of nick is needed to access
        # cache instead of making continous requests
        # that bring to flood
        gino = await bot.get_entity(gino_id)
    except FloodWaitError as e:
        return print(f"Too may request. {e}")
    cmd = Utils.status_commands[2].get("🌡️ temp")
    temp = await Utils._exec(gino_id, cmd=cmd, name="🌡️ temp")
    temp = Utils.get_temperature(temp)
    temp = re.search(r"[0-9]+\.[0-9]+", temp).group(0)
    if float(temp) >= 50.00:
        await bot.send_message(gino, f"CPU TEMPERATURE WARNING: {temp}°C")


asyncio.run(journal_log())
