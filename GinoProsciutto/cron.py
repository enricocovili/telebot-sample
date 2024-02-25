from telethon import TelegramClient
from telethon.errors import FloodWaitError
from utils import Utils
import asyncio, subprocess, re

temp_limit = 52.00


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
    if float(temp) >= temp_limit:
        top_output = subprocess.check_output(["top", "-b", "-n", "1"]).decode("utf-8").split("\n")[6:13]
        cleared_output = []
        for line in top_output:
            line = line.split()
            # get only 1st, 2nd, 9th, 10th and 12th column of top output
            line = "{col0:<5}, {col1:<5}, {col8:<5}, {col9:<5}, {col11:>5}".format(col0=line[0], col1=line[1], col8=line[8], col9=line[9], col11=line[11])
            cleared_output.append(line)
        cleared_output = "\n".join(cleared_output)
        await bot.send_message(gino, f"CPU TEMPERATURE WARNING: {temp}°C\nMore info:\n{cleared_output}")
    # top -b -n 1 | head -n 15 | tail -n 9 | awk '{printf "%5s %5s %5s %5s %s\n", $1, $2, $9, $10, $12}'

asyncio.run(journal_log())
