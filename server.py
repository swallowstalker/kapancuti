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

load_dotenv(find_dotenv())

updater = Updater(token=os.getenv('BOT_TOKEN', 'suatu-token')) # dummy bot
dispatcher = updater.dispatcher

# locale.setlocale(locale.LC_ALL, 'id_ID')


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
print(holidays_collection)
print(len(list(holidays_collection.find())))


def year(bot, update):

    current_year = datetime.now().year

    yearly_holidays = holidays_collection.find({
        'foremost_date': {
            '$gte': datetime(current_year, 1, 1, tzinfo=JAKARTA_TIMEZONE),
            '$lt': datetime(current_year + 1, 1, 1, tzinfo=JAKARTA_TIMEZONE)
        }
    })

    message = "Berikut adalah hari libur untuk tahun {year}\n".format_map({'year': current_year})

    current_month = -1
    for holiday in yearly_holidays:
        foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)

        header_active = False
        if current_month != foremost_date.month:
            header_active = True
            current_month = foremost_date.month

        message += holiday_only_templating(holiday, header_active)
    
    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "year")


def track(update, bot, command):
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', "")
    user = update.message.from_user
    if admin_chat_id != "":
        bot.send_message(admin_chat_id, text="Called by {full_name} ({username}), command: {command}".format_map(
            {'username': user.username, 'full_name': user.full_name, 'command': command}))


def estimate(target_datetime=datetime.now(tz=JAKARTA_TIMEZONE)):
    diff = target_datetime - datetime.now(tz=JAKARTA_TIMEZONE)
    return format_timedelta(delta=diff, add_direction=True)


MONTH_HEADER_TEMPLATE = "----------------\n" \
                        "<b>{month_name}</b>\n"
HOLIDAY_ONLY_TEMPLATE = "({estimation})\n" \
                        "⚫ {holiday_date_string} (<b>{description}</b>)\n"


RECOMMENDATION_TEMPLATE = HOLIDAY_ONLY_TEMPLATE + "{recommendations}\n"
LEAVE_RECOMMENDATION_TEMPLATE = "Rekomendasi cuti ({total_leave} hari cuti, {total_holiday_plus_leave} libur)\n" \
                                "{leave_recommendation_date_list}" \
                                "Liburan dari {holiday_plus_leave_start} - {holiday_plus_leave_end}\n"


def holiday_only_templating(holiday, header_active=False):
    foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)
    message = ''
    if header_active:
        message += MONTH_HEADER_TEMPLATE.format_map({'month_name': foremost_date.strftime('%B %Y')})

    message += HOLIDAY_ONLY_TEMPLATE.format_map({
        'estimation': estimate(holiday['foremost_date']),
        'holiday_date_string': foremost_date.strftime('%A %d %b'),
        'description': holiday['description']
    })

    return message


def recommendation_templating(holiday, header_active=False):
    foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)
    message = ''
    if header_active:
        message += MONTH_HEADER_TEMPLATE.format_map({'month_name': foremost_date.strftime('%B %Y')})
        message += "----------------\n"

    total_leave = len(holiday['leave_recommendation'])
    if total_leave > 0:
        holiday_streak_start = holiday['holiday_streak']['start'].astimezone(JAKARTA_TIMEZONE)
        holiday_streak_end = holiday['holiday_streak']['end'].astimezone(JAKARTA_TIMEZONE)

        holiday_streak_delta = holiday_streak_end - holiday_streak_start
        total_holiday_plus_leave = format_timedelta(delta=holiday_streak_delta)

        leave_recommendation_date_list = ''
        for leave in holiday['leave_recommendation']:
            leave_recommendation_date_list += "☉ " + leave.astimezone(JAKARTA_TIMEZONE).strftime('%A %d %b') + "\n"

        recommendation_submessage = LEAVE_RECOMMENDATION_TEMPLATE.format_map({
            'total_leave': total_leave,
            'total_holiday_plus_leave': total_holiday_plus_leave,
            'leave_recommendation_date_list': leave_recommendation_date_list,
            'holiday_plus_leave_start': holiday_streak_start.strftime('%A %d %b'),
            'holiday_plus_leave_end': holiday_streak_end.strftime('%A %d %b')
        })
    else:
        recommendation_submessage = 'Tidak ada rekomendasi cuti\n\n'

    message += RECOMMENDATION_TEMPLATE.format_map({
        'estimation': estimate(holiday['foremost_date']),
        'holiday_date_string': foremost_date.strftime('%A %d %b'),
        'description': holiday['description'],
        'recommendations': recommendation_submessage
    })
    return message


def incoming(bot, update):

    current_time = datetime.now().astimezone(tz=JAKARTA_TIMEZONE)
    max_incoming_time = current_time + timedelta(days=91)

    yearly_holidays = holidays_collection.find({
        'foremost_date': {
            '$gte': current_time,
            '$lt': max_incoming_time
        }
    })

    message = "Berikut adalah hari libur untuk 3 bulan yang akan datang\n"

    current_month = -1
    for holiday in yearly_holidays:
        foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)

        header_active = False
        if current_month != foremost_date.month:
            header_active = True
            current_month = foremost_date.month

        message += holiday_only_templating(holiday, header_active)

    message += '\nUntuk melihat rekomendasi cuti, silakan panggil /recommendation\n'

    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "incoming")


def recommendation(bot, update):

    current_time = datetime.now().astimezone(tz=JAKARTA_TIMEZONE)
    max_incoming_time = current_time + timedelta(days=91)

    yearly_holidays = holidays_collection.find({
        'foremost_date': {
            '$gte': current_time,
            '$lt': max_incoming_time
        }
    })

    message = "Berikut adalah hari libur dan rekomendasi cuti untuk 3 bulan mendatang\n"

    current_month = -1
    for holiday in yearly_holidays:
        foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)

        header_active = False
        if current_month != foremost_date.month:
            header_active = True
            current_month = foremost_date.month

        message += recommendation_templating(holiday, header_active)

    bot.send_message(update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
    track(update, bot, "recommendation")


year_handler = CommandHandler('year', year)
dispatcher.add_handler(year_handler)

incoming_handler = CommandHandler('incoming', incoming)
dispatcher.add_handler(incoming_handler)

recommendation_handler = CommandHandler('recommendation', recommendation)
dispatcher.add_handler(recommendation_handler)


if __name__ == "__main__":
    print("Running kapancuti server")
    updater.start_polling(poll_interval=7, clean=True)
