import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Utils:

    TOKEN = os.getenv('BOT_TOKEN')

    out_tmpl_ytdl = Path('tmp_song/%(title)s.mp3')

    ydl_opts = {
        'format': 'bestaudio',
        'logtostderr': False,
        'quiet': True,
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'outtmpl': str(out_tmpl_ytdl),
        'nooverwrites': False,
    }
