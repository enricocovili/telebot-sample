import requests
import telebot
import youtube_dl
from pathlib import Path
from requests import get
from utils import Utils

bot = telebot.TeleBot(Utils.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_author(message):
    bot.reply_to(
        message,
        ('🇮🇹 Pizza Pasta Mandolino 🇮🇹,'
         'Made by @ilginop,').replace(',', '\n'),
    )


# a cursed shaggy image


@bot.message_handler(commands=["shaggy"])
def shaggy_message(message):

    # MARKUP TESTS
    # markup = telebot.types.ReplyKeyboardMarkup(
    #     row_width=3, resize_keyboard=True, one_time_keyboard=True)

    # # Creates a 3x3 table for KeyboardButton
    # for i in range(3):
    #     util = []
    #     [ util.append(telebot.types.KeyboardButton('a')) for j in range(3) ]
    #     markup.add(*util)  # passes the list as separated items
    bot.send_photo(message.chat.id, open(
        'shaggy.jpeg', 'rb'))

# manage all !pornhub messages


@bot.message_handler(commands=["pornhub"])
def handle_message(message):
    handeld_message = message.text[9:]
    bot.reply_to(
        message, 'https://www.pornhub.com/video/search?search=' +
        handeld_message.replace(' ', '+'))


@bot.message_handler(commands=["yt"])
def yt_download(message):
    bot.send_message(message.chat.id, text=" 📥 Downloading... 📥")
    msg = str(message.text[4:])
    if not len(msg):
        return bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id + 1,
            text="Write the name of the song after the command!\n"
                 "(example: /yt despacito)")
    url = get_url(msg)
    youtube_dl.YoutubeDL(Utils.ydl_opts).download([url])
    # get a list of all the files in tmp_song, and takes only the first one
    # Spoiler: there is only one file in it because yt_dl download
    # changes some characters sometimes (idk how it works)
    file_path = list(Path('tmp_song').rglob('*'))
    bot.send_audio(message.chat.id, audio=open(
        file_path[0], 'rb'), caption=file_path[0].name)
    bot.delete_message(message.chat.id, message.message_id + 1)
    [file.unlink() for file in file_path]  # clear tmp_song (debugging reason)
    return


def get_url(msg):
    try:
        video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
            msg, download=False)
        url = msg
    except Exception:
        msg = "ytsearch:" + msg
        video_info = youtube_dl.YoutubeDL(Utils.ydl_opts).extract_info(
            msg, download=False)
        url = video_info.get('entries')[0].get('webpage_url')
    return url


@bot.message_handler(commands=['getip'])
def get_ip(message):
    bot.send_message(message.chat.id, text="User:")
    bot.register_next_step_handler(message, user_check)

def user_check(message):
    if message.text == Utils.USER:
        bot.reply_to( message, 'Password:')
        return bot.register_next_step_handler(message, password_check)
    # bot.delete_message(message.chat.id, message.message_id+1)
    [ bot.delete_message(message.chat.id, message.message_id - i) for i in reversed(range(0,2))]
    bot.send_message(message.chat.id,text='❌ Wrong user ❌')

def password_check(message):
    if message.text == Utils.PASSWORD:
        ip = get('https://api.ipify.org').text
        return bot.reply_to(message, f'Ip address: {ip}')
    else:
        [ bot.delete_message(message.chat.id, message.message_id - i) for i in reversed(range(0,4))]
        bot.send_message(message.chat.id, '❌ Wrong password ❌')

# This shit is needed because if i forget how to handle
# all other message i don't need to search in doc


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

bot.enable_save_next_step_handlers()
bot.load_next_step_handlers()
bot.polling()
