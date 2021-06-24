import telebot
import youtube_dl
from pathlib import Path

from youtube_dl import utils
from utils import Utils

bot = telebot.TeleBot(Utils.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_author(message):
    bot.reply_to(
        message,
        ('Comandi disponibili:,'
         '/yt -> scaricare canzoni da youtube,'
         '/pornhub -> lo scopri (Inserisci un nome insieme al comando),'
         '/shaggy -> foto di shaggy,'
         'Made by @ilginop,').replace(',', '\n')
    )


'''
This shit is needed because if i forget how to handle all other message i don't need to search in doc
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)
'''

# a cursed shaggy image


@bot.message_handler(commands=["shaggy"])
def shaggy_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=3, resize_keyboard=True, one_time_keyboard=True)

    # Creates a 3x3 table for KeyboardButton
    for i in range(3):
        util = []
        for j in range(3):
            util.append(telebot.types.KeyboardButton('a'))
        markup.add(*util)  # passes the list as separated items
    bot.send_photo(message.chat.id, open(
        'shaggy.jpeg', 'rb'), reply_markup=markup)

# manage all !pornhub messages


@bot.message_handler(commands=["pornhub"])
def handle_message(message):
    handeld_message = message.text[9:]
    bot.reply_to(
        message, 'https://www.pornhub.com/video/search?search=' +
        handeld_message.replace(' ', '+'))


@bot.message_handler(commands=["yt"])
def yt_download(message):
    msg = bot.reply_to(message, "Inserire link youtube: ")
    bot.register_next_step_handler(msg, real_download)
    return


def real_download(message):
    bot.send_message(message.chat.id, text=" 📥 Downloading... 📥")
    msg = message.text
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
    bot.send_audio(message.chat.id, audio=open(
        file_path[0], 'rb'), caption=url)
    bot.delete_message(message.chat.id, message.message_id + 1)
    # clear tmp_song (debugging reason)
    [file.unlink() for file in file_path]
    return


bot.polling()
