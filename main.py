import os
import telebot
import youtube_dl
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

ydl_opts = {
    'format': 'bestaudio',
    'logtostderr': False,
    'quiet': True,
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'outtmpl': 'a.mp3',
    'nooverwrites': False,
}


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_author(message):
    bot.reply_to(message,
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
    mklist = []
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=3, resize_keyboard=True, one_time_keyboard=True)

    # Creates a 3x3 table for KeyboardButton
    for i in range(3):
        util = []
        for j in range(3):
            util.append(telebot.types.KeyboardButton('a'))
        mklist.append(util)
        markup.add(*mklist[i])  # passes the list as separated items
    bot.send_photo(message.chat.id, open(
        'shaggy.jpeg', 'rb'), reply_markup=markup)
    #

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
    # print(message.text)
    bot.send_message(message.chat.id, " 📥 Downloading... 📥")
    msg = message.text
    try:
        video_info = youtube_dl.YoutubeDL(ydl_opts).extract_info(
            msg, download=False)
        title = video_info.get('title', None)
        url = msg
    except:
        msg = "ytsearch:" + msg
        video_info = youtube_dl.YoutubeDL(ydl_opts).extract_info(
            msg, download=False)
        title = video_info['entries'][0].get('title', None)
        url = video_info['entries'][0].get('webpage_url', None)
    # bot.send_message(message.chat.id, "asdasd")
    youtube_dl.YoutubeDL(ydl_opts).download([url])
    bot.send_audio(message.chat.id, audio=open(
        'a.mp3', 'rb'), title=title)
    bot.delete_message(message.chat.id, message.message_id + 1)
    os.remove('a.mp3')
    return


bot.polling()
