from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import locale
import os
from dotenv import load_dotenv, find_dotenv
import handler
import pprint

load_dotenv(find_dotenv())

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

response_handler = handler.ResponseHandler()


def help(bot, update):
    show_options(update)
    track(update, bot, "help")


def show_options(query):
    keyboard = [
        [
            InlineKeyboardButton("Liburan mendatang", callback_data='incoming'),
            InlineKeyboardButton("Rekomendasi cuti", callback_data='recommendation')
        ],
        [
            InlineKeyboardButton("Liburan per tahun", callback_data='year'),
            InlineKeyboardButton("Tentang bot", callback_data='about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Silakan pilih tipe info liburan', reply_markup=reply_markup)


def callback_handler(bot, update):
    query = update.callback_query

    if query.data == 'incoming':
        incoming(bot, query)
        show_options(query)
    elif query.data == 'recommendation':
        recommendation(bot, query)
        show_options(query)
    elif query.data == 'year':
        show_year_options(query)
    elif query.data[:5] == 'year_':
        year(bot, query, [query.data[5:]])
        show_options(query)
    elif query.data == 'about':
        about(bot, query)
        show_options(query)


def show_year_options(query):
    keyboard = [
        [InlineKeyboardButton("2018", callback_data='year_2018')],
        [InlineKeyboardButton("2019", callback_data='year_2019')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Silakan pilih tahun', reply_markup=reply_markup)


def year(bot, query, args):

    year = args[0] if len(args) > 0 else None
    message = response_handler.year(year)

    bot.send_message(query.message.chat_id,
                     text=message,
                     parse_mode=ParseMode.HTML)

    track(query, bot, "year")


def incoming(bot, query):

    message = response_handler.incoming()
    bot.send_message(query.message.chat_id,
                     text=message,
                     parse_mode=ParseMode.HTML)

    track(query, bot, "incoming")


def recommendation(bot, query):
    message = response_handler.recommendation()
    bot.send_message(query.message.chat_id,
                     text=message,
                     parse_mode=ParseMode.HTML)

    track(query, bot, "recommendation")


def about(bot, query):
    message = response_handler.help()
    bot.send_message(query.message.chat_id,
                     text=message,
                     parse_mode=ParseMode.HTML)

    track(query, bot, "about")


def track(update, bot, command):
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', "")

    user = update.message.chat
    full_name = str(user.first_name) + " " + str(user.last_name)
    if admin_chat_id != "":
        bot.send_message(admin_chat_id, text="Called by {full_name} ({username}), command: {command}".format_map(
            {'username': user.username, 'full_name': full_name, 'command': command}))


def main():
    updater = Updater(token=os.getenv('BOT_TOKEN', 'suatu-token'))  # dummy bot
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', help)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    inline_handler = CallbackQueryHandler(callback_handler)
    dispatcher.add_handler(inline_handler)

    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

    updater.start_polling(poll_interval=7, clean=True)


if __name__ == "__main__":
    print("Running kapancuti server")
    main()
