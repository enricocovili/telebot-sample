import os
from dotenv import load_dotenv
from pathlib import Path
import youtube_dl

load_dotenv()


class Utils:

    TOKEN = os.getenv("BOT_TOKEN")
    APP_ID = os.getenv("APP_ID")
    APP_HASH = os.getenv("APP_HASH")
    USER = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
    GINO_ID = int(os.getenv("GINO_ID"))

    out_tmpl_ytdl = Path("tmp_song/%(title)s.mp3")

    ydl_opts = {
        "format": "bestaudio",
        "logtostderr": False,
        "quiet": True,
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "outtmpl": str(out_tmpl_ytdl),
        "nooverwrites": False,
    }

    def get_url(msg):
        try:
            video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
                msg, download=False
            )
            url = msg
        except youtube_dl.utils.DownloadError:
            # print(e)
            msg = "ytsearch:" + msg
            try:
                video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
                    msg, download=False
                )
            except youtube_dl.utils.DownloadError:
                return 1
            url = video_info.get("entries")[0].get("webpage_url")
        except Exception:
            return 1
        return url
