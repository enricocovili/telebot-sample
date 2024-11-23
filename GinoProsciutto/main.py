from telethon import events
from utils import Utils
from handlers import *
import logging

# setup logging to file
logging.basicConfig(
    # filename="logs/bot.log",
    # filemode="a+",
    format="%(asctime)s:%(levelname)s:%(name)s -> %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
)

bot = client.bot


@bot.on(events.NewMessage(pattern=Utils.pattern_constructor(["help", "start"])))
async def send_author(event):
    await event.reply(
        ("🇮🇹 Pizza Pasta Mandolino 🇮🇹," "Made by @ilginop,").replace(",", "\n")
    )


@bot.on(events.NewMessage(pattern="/shaggy"))
async def shaggy(event):
    await bot.send_file(event.chat, "./shaggy.jpeg", caption="Shaggy")


if __name__ == "__main__":
    # clear tmp_song
    [file.unlink() for file in Utils.out_tmpl_ytdl.parent.glob("*")]

    logging.info("tmp_song cleared")

    bot.add_event_handler(yt_dwnld.yt_download)
    bot.add_event_handler(yt_dwnld.callback)
    bot.add_event_handler(menu.callback)
    bot.add_event_handler(menu.menu)
    bot.add_event_handler(menu.pistatus)
    bot.add_event_handler(others.exec)
    bot.add_event_handler(others.classifica_artiglio)

    logging.info(f"commands loaded")

    bot.start(bot_token=Utils.TOKEN)
    # load_commands(bot)
    bot.run_until_disconnected()
