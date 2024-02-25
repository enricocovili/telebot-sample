from telethon import events, Button
import yt_dlp
from utils import Utils
from pathlib import Path
import logging


@events.register(events.NewMessage(pattern="/yt"))
async def yt_download(event):
    bot = event.client
    response = await bot.send_message(
        event.chat, message=" 📥 Downloading... 📥"
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
    logging.info("received: yt-download " + url)
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
