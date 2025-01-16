import json
from dotenv import load_dotenv
from pathlib import Path
import yt_dlp
import re
import subprocess

load_dotenv()


class Utils:
    with open("config.json", "r") as f:
        config = json.load(f)

    TOKEN = config.get("BOT_TOKEN")
    APP_ID = config.get("APP_ID")
    APP_HASH = config.get("APP_HASH")
    WHITELIST_IDS = config.get("WHITELIST_IDS")
    artiglio_ranking_url = config.get("volley_ranking_url")

    out_tmpl_ytdl = Path("tmp_song/%(title)s")

    ydl_opts = {
        "logtostderr": True,
        "quiet": True,
        "external_downloader_args": ["-loglevel", "panic"],
        "outtmpl": str(out_tmpl_ytdl),
        "nooverwrites": False,
    }

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

    def pattern_constructor(patterns: list):
        return r"".join(f"(/{pattern})|" for pattern in patterns)[:-1]

    def get_url(msg):
        yt_re = re.compile(
            r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        )
        if yt_re.match(msg):
            return msg.split("?")[0]
        msg = f"ytsearch:{msg}"
        with yt_dlp.YoutubeDL(Utils.ydl_opts) as ydl:
            url = ydl.extract_info(msg, download=False)
        final_url = url["entries"][0]["webpage_url"]
        final_url = final_url.split("?")[0]
        return final_url

    def get_temperature(full_temp):
        reducedtemp = full_temp.split()[-1]
        reducedtemp = f"{reducedtemp[:2]}.{reducedtemp[2:-1]}°C\n"
        return f"{' '.join(full_temp.split()[:-1])} {reducedtemp}"

    async def _exec(chat_id, cmd, name=""):
        if not cmd:
            return "No command specified"
        if chat_id not in Utils.WHITELIST_IDS:
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
