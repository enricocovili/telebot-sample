from telethon import events
from utils import Utils
import handlers.client, handlers.yt_dwnld, handlers.exec, handlers.menu

bot = handlers.client.bot
# event: events.newmessage.NewMessage.Event


@bot.on(events.NewMessage(pattern=Utils.pattern_constructor(["help", "start"])))
async def send_author(event):
    await event.reply(
        ("🇮🇹 Pizza Pasta Mandolino 🇮🇹," "Made by @ilginop,").replace(",", "\n")
    )


@bot.on(events.NewMessage(pattern="/shaggy"))
async def shaggy(event):
    await bot.send_file(event.chat, "./shaggy.jpeg", caption="Shaggy")


@bot.on(events.NewMessage(pattern="/pornhub"))
async def pornhub(event):
    handeld_message = event.text[9:]
    await bot.send_message(
        event.chat,
        "https://www.pornhub.com/video/search?search="
        + handeld_message.replace(" ", "+"),
    )


with bot as client:
    client.add_event_handler(handlers.yt_dwnld.yt_download)
    client.add_event_handler(handlers.exec.exec)
    client.add_event_handler(handlers.menu.callback)
    client.add_event_handler(handlers.menu.menu)
    client.add_event_handler(handlers.menu.pistatus)
print(f"{'-'*30}\ncommands loaded, bot online\n{'-'*30}")

"""

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# print(message.text.replace)
# bot.reply_to(message, message.text)


"""

if __name__ == "__main__":
    bot.start(bot_token=Utils.TOKEN)
    bot.run_until_disconnected()
