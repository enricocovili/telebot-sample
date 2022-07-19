from utils import Utils
from telethon import events
import telethon


@events.register(events.NewMessage(pattern="/film"))
async def film(event: events.newmessage.NewMessage.Event):
    fileName = ""

    async def callback(current, total):
        if current == total:
            await Utils._exec(event.chat_id, cmd=["sudo", "mount", "-a"])
            # move the downloaded file to /SFTP/sftp_user/1TbUSB/
            await Utils._exec(
                event.chat_id,
                cmd=["sudo", "mv", f"./{fileName}", "/SFTP/sftp_user/1TbUSB/"],
            )
            print("done")

    async with event.client.conversation(event.chat) as conv:
        await conv.send_message("Please forward me a message containing film")
        filmMsg: telethon.types.Message = await conv.get_response()

        if filmMsg.media:
            fileName = filmMsg.text
            # and hasattr(filmMsg.media, "document")
            # download the file
            await event.client.download_media(
                filmMsg.media,
                f"./{fileName}",
                progress_callback=callback,
            )
            # await event.reply(filmMsg.media.title)
        else:
            await event.reply("No valid media found")
