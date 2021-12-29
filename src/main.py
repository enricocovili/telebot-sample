from telethon import events, Button
from utils import Utils
import subprocess
import handlers.client, handlers.yt_dwnld

bot = handlers.client.bot
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


with bot as client:
    client.add_event_handler(handlers.yt_dwnld.yt_download)


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


@bot.on(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    msg = event.text.split()[1:]
    out = await _exec(event, cmd=msg)
    await event.reply(out[:4000])


@bot.on(events.NewMessage(pattern="/pistatus"))
async def pistatus(event: events.newmessage.NewMessage.Event):
    output = ""
    for i in status_commands:
        for key, value in i.items():
            if key == "🌡️ temp":
                # also with "🌡️ temp" part
                full_temp = await _exec(event, cmd=value, name=key)
                # only number
                reducedtemp = full_temp.split()[-1]
                reducedtemp = f"{reducedtemp[:2]}.{reducedtemp[2:-1]}°C\n"
                full_temp = f"{' '.join(full_temp.split()[:-1])} {reducedtemp}"
                output += full_temp
            else:
                output += await _exec(event, cmd=value, name=key)
    await event.reply(output[:4000])


@bot.on(events.CallbackQuery)
async def callback(event):
    # print(event.data)
    if event.data == b"reload_usb":
        await _exec(event, ["sudo", "mount", "-a"])
    elif event.data == b"general_status":
        await pistatus(event)


@bot.on(events.NewMessage(pattern="/menu"))
async def menu(event: events.newmessage.NewMessage):
    # chat = await event.get_chat()
    sender = await event.get_sender()
    await bot.send_message(
        sender,
        message="Select one of the options below:",
        buttons=[
            [
                Button.inline("reload_usb", data=b"reload_usb"),
                Button.inline("general_status", data=b"general_status"),
            ],
        ],
    )


"""

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# print(message.text.replace)
# bot.reply_to(message, message.text)


"""

bot.start(bot_token=Utils.TOKEN)
bot.run_until_disconnected()
