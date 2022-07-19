from telethon import TelegramClient
from utils import Utils

bot = TelegramClient(
    "session",
    api_id=Utils.APP_ID,
    api_hash=Utils.APP_HASH,
)
