import telebot
import youtube_dl
from pathlib import Path

from utils import Utils


class MainBot():
    '''
    Instantiates the bot
    '''
    def __init__(self) -> None:
        '''
        Contains the list of the functions (commands)
        of the bot
        '''
        self.bot = telebot.TeleBot(Utils.TOKEN)

        @self.bot.message_handler(commands=['start', 'help'])
        def _send_author(message):
            self.send_author(message)

        '''
        This shit is needed because if i forget how to handle
        all other message i don't need to search in doc
        @bot.message_handler(func=lambda message: True)
        def echo_all(message):
            bot.reply_to(message, message.text)
        '''

        # a cursed shaggy image

        @self.bot.message_handler(commands=["shaggy"])
        def _shaggy_message(message):
            self.shaggy_message(message)

        # manage all !pornhub messages

        @self.bot.message_handler(commands=["pornhub"])
        def _pornhub(message):
            self.pornhub(message)

        @self.bot.message_handler(commands=["yt"])
        def _yt_download(message):
            self.yt_download(message)

    def start(self):
        self.bot.polling()

    def send_author(self, message):
        self.bot.reply_to(
            message,
            ('❗ I comandi con * richiedono un nome dopo il comando ❗,'
             'Comandi disponibili:,'
             '🔺 /yt -> * scaricare canzoni da youtube,'
             '🔺 /pornhub -> * lo scopri,'
             '🔺 /shaggy -> foto di shaggy,'
             'Made by @ilginop,').replace(',', '\n')
        )

    def shaggy_message(self, message):
        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=3, resize_keyboard=True, one_time_keyboard=True)

        # Creates a 3x3 table for KeyboardButton
        for i in range(3):
            util = []
            for j in range(3):
                util.append(telebot.types.KeyboardButton('a'))
            markup.add(*util)  # passes the list as separated items
        self.bot.send_photo(message.chat.id, open(
            'shaggy.jpeg', 'rb'), reply_markup=markup)

    def pornhub(self, message):
        handeld_message = message.text[9:]
        self.bot.reply_to(
            message, 'https://www.pornhub.com/video/search?search=' +
            handeld_message.replace(' ', '+'))

    def yt_download(self, message):
        self.bot.send_message(message.chat.id, text=" 📥 Downloading... 📥")
        msg = str(message.text[4:])
        if not len(msg):
            return self.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id + 1,
                text="Not a valid link")
        try:
            video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
                msg, download=False)
            url = msg
        except Exception:
            msg = "ytsearch:" + msg
            video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
                msg, download=False)
            url = video_info.get('entries')[0].get('webpage_url')

        youtube_dl.YoutubeDL(Utils.ydl_opts).download([url])
        # get a list of all the files in tmp_song, and takes only the first one
        # Spoiler: there is only one file in it because yt_dl download
        # changes some characters sometimes (idk how it works)
        file_path = list(Path('tmp_song').rglob('*'))
        self.bot.send_audio(message.chat.id, audio=open(
            file_path[0], 'rb'), caption=file_path[0].name)
        self.bot.delete_message(message.chat.id, message.message_id + 1)
        # clear tmp_song (debugging reason)
        [file.unlink() for file in file_path]
        return


bot = MainBot()
bot.start()