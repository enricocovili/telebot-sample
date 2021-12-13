import os
from dotenv import load_dotenv
from pathlib import Path
import yt_dlp
import re

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
        "logtostderr": True,
        "quiet": False,
        "outtmpl": str(out_tmpl_ytdl),
        "nooverwrites": False,
    }

    def pattern_constructor(patterns: list):
        return r"".join(f"(/{pattern})|" for pattern in patterns)[:-1]

    def get_url(msg):
        yt_re = re.compile(
            r"/(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/).+/gmi"
        )
        if yt_re.match(msg):
            return msg
        msg = f"ytsearch:{msg}"
        with yt_dlp.YoutubeDL(Utils.ydl_opts) as ydl:
            url = ydl.extract_info(msg, download=False)
        return url["entries"][0]["webpage_url"]
