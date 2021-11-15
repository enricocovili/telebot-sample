from telethon import TelegramClient, events
import asyncio
import youtube_dl
from pathlib import Path
from utils import Utils
import subprocess

# event: events.newmessage.NewMessage.Event


def pattern_constructor(patterns: list):
    res = [r"".join(f"(/{pattern})|" for pattern in patterns)][0]
    return res[:-1]


bot = TelegramClient("bot", api_id=Utils.APP_ID, api_hash=Utils.APP_HASH).start(
    bot_token=Utils.TOKEN
)


@bot.on(events.NewMessage(pattern=pattern_constructor(["help", "start"])))
async def send_author(event):
    await event.reply(
        ("🇮🇹 Pizza Pasta Mandolino 🇮🇹," "Made by @ilginop,").replace(",", "\n"),
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
    await asyncio.sleep(1)
    msg = " ".join(event.text.split()[1:])
    if not len(msg):
        return await bot.edit_message(
            event.chat,
            message=response,
            text="❗Write the name of the song after the command❗\n"
            "(example: /yt despacito)",
        )
    # url = Utils.get_url(msg)
    if "error" in msg:
        return await bot.edit_message(
            event.chat, message=response, text="❌ An error occured ❌"
        )
    # youtube_dl.YoutubeDL(Utils.ydl_opts).download([url])
    # get a list of all the files in tmp_song, and takes only the first one
    # Spoiler: there is only one file in it because yt_dl download
    # changes some characters sometimes (idk how it works)
    # file_path = list(Path("tmp_song").rglob("*"))
    # bot.send_audio(
    #     event.chat.id,
    #     audio=open(file_path[0], "rb"),
    #     caption=file_path[0].name,
    # )
    await response.delete()
    # [file.unlink() for file in file_path]  # clear tmp_song (debugging reason)
    return


@bot.on(events.NewMessage(pattern="/netstats"))
async def netstats(event):
    msg = event.text.split()
    if len(msg) != 3 or msg[1] != Utils.USER or msg[2] != Utils.PASSWORD:
        await bot.send_message(event.chat, "❌ Invalid Username/Password ❌")
    else:
        output = subprocess.check_output(["net-info.sh"]).decode("utf-8")
        await bot.send_message(
            event.chat,
            output,
        )
    await event.message.delete()
    return


@bot.on(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    if event.chat_id != Utils.GINO_ID:
        return
    msg = event.text.split()
    del msg[0]
    try:
        output = subprocess.check_output([*msg]).decode("utf-8")
    except Exception as e:
        output = e

    await event.reply(output)


"""
# This shit is needed because if i forget how to handle
# all other message i don't need to search in doc


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# print(message.text.replace)
# bot.reply_to(message, message.text)


# bot.enable_save_next_step_handlers()
# bot.load_next_step_handlers()
# bot.polling()
"""

bot.run_until_disconnected()
