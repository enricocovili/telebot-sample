from telethon import events, Button
import yt_dlp
from utils import Utils
from pathlib import Path
import logging


async def download_and_clean(url: str, event: events.newmessage.NewMessage):
    msg = await event.get_message()
    await event.client.edit_message(event.chat, message=msg, text="Downloading...")
    yt_dlp.YoutubeDL(Utils.ydl_opts).download([url])
    await event.client.edit_message(event.chat, message=msg, text="Uploading...")
    # get a list of all the files in tmp_song, and takes only the first one
    # Spoiler: there is only one file in it because yt_dl download
    # changes some characters sometimes (idk how it works)
    file_path = list(Path("tmp_song").rglob("*"))
    await event.client.send_message(
        event.chat,
        file=file_path[0],
        buttons=event.client.build_reply_markup(Button.url("🔗 YT link 🔗", url=url)),
    )
    await event.client.delete_messages(event.chat, msg)
    [file.unlink() for file in file_path]  # clear ./tmp_song (debug reason)
    return


@events.register(events.CallbackQuery)
async def callback(event):
    format = event.data.split(b"|")[0].decode("utf-8")
    url = event.data.split(b"|")[1].decode("utf-8")
    logging.info(f"received: yt-download {format} {url}")
    if format == "yt_audio":
        Utils.ydl_opts["format"] = "bestaudio"
        Utils.ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
        await event.answer("Downloading audio...")
    elif format == "yt_video":
        Utils.ydl_opts["postprocessors"] = []
        # best video up to 480p, best audio
        Utils.ydl_opts["format"] = "bv*[height<=480]+ba/b[height<=480] / wv*+ba/w"
        Utils.ydl_opts["merge_output_format"] = "mp4"
        await event.answer("Downloading video...")
    else:
        # delete the message
        await event.delete()
        return await event.client.send_message(
            event.chat, message="❌ An error occured ❌"
        )

    await download_and_clean(url, event)


@events.register(events.NewMessage(pattern="/yt"))
async def yt_download(event):
    bot = event.client
    response = await bot.send_message(event.chat, message="🔍 Retreiving info... 🔍")
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
    with yt_dlp.YoutubeDL(Utils.ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info["title"]
        author = info["uploader"]
    # ask user if he wants to download audio or video
    await bot.edit_message(
        event.chat,
        message=response,
        text=f"Song found:\n🎵 {title} 🎵\nby 🎤 {author} 🎤",
        buttons=[
            [
                Button.inline("🔊 Audio 🔊", data=f"yt_audio|{url}"),
                Button.inline("🎥 Video 🎥", data=f"yt_video|{url}"),
            ]
        ],
    )
