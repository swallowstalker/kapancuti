from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from pymongo import MongoClient
from bson.codec_options import CodecOptions
from datetime import datetime, timedelta
from dateutil import tz
from babel.dates import format_timedelta
import locale
import os
from dotenv import load_dotenv, find_dotenv
import handler
import templater

load_dotenv(find_dotenv())

updater = Updater(token=os.getenv('BOT_TOKEN', 'suatu-token')) # dummy bot
dispatcher = updater.dispatcher

locale.setlocale(locale.LC_ALL, 'id_ID')


def help(bot, update):
    guide_message = """
Untuk menjaga keseimbangan kerja dan liburan, bot ini dibuat sebagai referensi untuk pengambilan cuti anda. 
Ada 3 command, yaitu: 

/year [tahun] 
/incoming 
/recommendation

Silakan dicoba.
Kritik dan saran silakan hubungi @swallowstalker ya.
    """

    bot.send_message(chat_id=update.message.chat_id, text=guide_message)


start_handler = CommandHandler('start', help)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)


JAKARTA_TIMEZONE = tz.gettz('Asia/Jakarta')

db = MongoClient(host=os.getenv('MONGO_HOST', "localhost"), port=int(os.getenv('MONGO_PORT', 27017))).get_database("kapancuti")
holidays_collection = db.get_collection('holidays', codec_options=CodecOptions(tz_aware=True))
print(holidays_collection.count())

response_handler = handler.ResponseHandler()


def year(bot, update):
    message = response_handler.year()
    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "year")


def incoming(bot, update):
    message = response_handler.incoming()
    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "incoming")


def recommendation(bot, update):
    message = response_handler.recommendation()
    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "recommendation")


def track(update, bot, command):
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', "")
    user = update.message.from_user
    if admin_chat_id != "":
        bot.send_message(admin_chat_id, text="Called by {full_name} ({username}), command: {command}".format_map(
            {'username': user.username, 'full_name': user.full_name, 'command': command}))


year_handler = CommandHandler('year', year)
dispatcher.add_handler(year_handler)

incoming_handler = CommandHandler('incoming', incoming)
dispatcher.add_handler(incoming_handler)

recommendation_handler = CommandHandler('recommendation', recommendation)
dispatcher.add_handler(recommendation_handler)


if __name__ == "__main__":
    print("Running kapancuti server")
    updater.start_polling(poll_interval=7, clean=True)
