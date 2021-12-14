from telethon import TelegramClient, events, Button
import yt_dlp
from pathlib import Path
from utils import Utils
import subprocess

# event: events.newmessage.NewMessage.Event

status_commands = [
    # ["uname", "-a"],
    {"🕐 uptime": ["uptime", "-p"]},
    {"📊 load": ["cat", "/proc/loadavg"]},
    # {"📊 mem": ["cat", "/proc/meminfo"]},
    {"🌡️ temp": ["cat", "/sys/class/thermal/thermal_zone0/temp"]},
    # ["df", "-h"],
    # ["pihole", "status"],
    {"tgram_bot": ["systemctl", "is-active", "telegram_bot_py"]},
    {"lavalink_server": ["systemctl", "is-active", "lavalink_server"]},
    {"discord_bot": ["systemctl", "is-active", "discord_bot_py"]},
]

bot = TelegramClient(
    "bot",
    api_id=Utils.APP_ID,
    api_hash=Utils.APP_HASH,
).start(bot_token=Utils.TOKEN)


async def _exec(event, cmd, name=""):
    if not cmd:
        return "No command specified"
    if event.chat_id != Utils.GINO_ID:
        return "❌ You are not allowed to use this command ❌"
    try:
        output = subprocess.run(
            [*cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as e:
        return f"❌ {e}"
    out = output.stdout if output.stdout else output.stderr
    return name + ": " + out if name else out


@bot.on(events.NewMessage(pattern=Utils.pattern_constructor(["help", "start"])))
async def send_author(event):
    await event.reply(
        ("🇮🇹 Pizza Pasta Mandolino 🇮🇹," "Made by @ilginop,").replace(",", "\n")
    )
    return


@bot.on(events.NewMessage(pattern="/shaggy"))
async def shaggy(event):
    await bot.send_file(event.chat, "./shaggy.jpeg", caption="Shaggy")
    return


@bot.on(events.NewMessage(pattern="/pornhub"))
async def pornhub(event):
    handeld_message = event.text[9:]
    await bot.send_message(
        event.chat,
        "https://www.pornhub.com/video/search?search="
        + handeld_message.replace(" ", "+"),
    )
    return


@bot.on(events.NewMessage(pattern="/yt"))
async def yt_download(event):
    response = await bot.send_message(
        event.chat, message=" 📥 (testing purpose) Downloading... 📥"
    )
    msg = " ".join(event.text.split()[1:])
    if not len(msg):
        return await bot.edit_message(
            event.chat,
            message=response,
            text="❗Write the name of the song after the command❗\n"
            "(example: /yt despacito)",
        )
    url = Utils.get_url(msg)
    if "error" in msg:
        return await bot.edit_message(
            event.chat, message=response, text=f"{url}\n❌ An error occured ❌"
        )
    yt_dlp.YoutubeDL(Utils.ydl_opts).download([url])
    # get a list of all the files in tmp_song, and takes only the first one
    # Spoiler: there is only one file in it because yt_dl download
    # changes some characters sometimes (idk how it works)
    file_path = list(Path("tmp_song").rglob("*"))
    await bot.send_message(
        event.chat,
        file=file_path[0],
        buttons=bot.build_reply_markup(Button.url("🔗 YT link 🔗", url=url)),
    )
    await response.delete()
    [file.unlink() for file in file_path]  # clear ./tmp_song (debug reason)
    return


@bot.on(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    msg = event.text.split()[1:]
    await event.reply(
        await _exec(event, cmd=msg),
    )


@bot.on(events.NewMessage(pattern="/pistatus"))
async def pistatus(event: events.newmessage.NewMessage.Event):
    output = ""
    for i in status_commands:
        for key, value in i.items():
            output += await _exec(event, cmd=value, name=key)
    await event.reply(output)


"""

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# print(message.text.replace)
# bot.reply_to(message, message.text)


"""

bot.run_until_disconnected()
