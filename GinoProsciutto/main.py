from telethon import events
from utils import Utils
from handlers import *
import logging, schedule, time, asyncio, threading
from cronjob_monitor import journal_log
from quart import Quart, request
from telethon import types

# setup logging to file
logging.basicConfig(
    # filename="logs/bot.log",
    # filemode="a+",
    format="%(asctime)s:%(levelname)s:%(name)s -> %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
)

bot = client.bot
app = Quart(__name__)


loop = asyncio.get_event_loop()

@app.route("/watchtower-update", methods=["POST"])
async def watchtower_update():
    data = await request.get_data(as_text=True)
    logging.info(f"Received watchtower update: {data}")
    
    buttons = [
        [types.KeyboardButtonCallback(text="Update docker", data=b"update_docker")]
    ]
    
    await bot.send_message(
        Utils.WHITELIST_IDS[0], 
        f"📢 Watchtower Update:\n{data}",
        buttons=buttons
    )
    return "OK", 200

@bot.on(events.CallbackQuery(data=b"update_docker"))
async def handle_exec_command(event):
    await event.edit("⏳ Updating docker containers with Watchtower...")
    output = await Utils._exec(event.chat_id, "docker run --rm --name watchtower_singlerun --volume /var/run/docker.sock:/var/run/docker.sock nickfedor/watchtower -R".split(), name="Watchtower Update", notimeout=True)
    await event.delete()
    await bot.send_message(event.chat_id, f"📦 Watchtower Update Output:\n{output}")

def scheduler_loop():
    schedule.every(10).seconds.do(
        lambda: asyncio.run_coroutine_threadsafe(journal_log(bot), loop)
    )
    try:
        while True:
            # logging.info("executing scheduled job")
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in scheduler loop: {e}")


@bot.on(events.NewMessage(pattern=r"^/(help|start)$"))
async def send_author(event):
    await event.reply(
        ("🇮🇹 Pizza Pasta Mandolino 🇮🇹\nMade by @ilginop").replace(",", "\n")
    )


@bot.on(events.NewMessage(pattern="/shaggy"))
async def shaggy(event):
    await bot.send_file(event.chat, "./shaggy.jpeg", caption="Shaggy")


# callback for every message that is not a command
@bot.on(events.NewMessage())
async def callback(event):
    url = Utils.get_url(event.text, force_url=True)
    if not url:
        return
    await media_dwnld.download(event, url)


async def main():
    # clear tmp_song
    [file.unlink() for file in Utils.out_tmpl_ytdl.parent.glob("*")]

    logging.info("tmp_song cleared")

    bot.add_event_handler(media_dwnld.callback)

    bot.add_event_handler(menu.callback)
    bot.add_event_handler(menu.menu)
    bot.add_event_handler(menu.pistatus)
    bot.add_event_handler(menu.exec)

    bot.add_event_handler(artiglio.artiglio)

    bot.add_event_handler(minecraft_server.start_minecraft_server)
    bot.add_event_handler(minecraft_server.stop_minecraft_server)

    logging.info(f"commands loaded")

    await bot.start(bot_token=Utils.TOKEN)

    threading.Thread(target=scheduler_loop, daemon=True).start()

    await asyncio.gather(
        app.run_task(host="0.0.0.0", port=5000), 
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
