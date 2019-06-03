from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from bson.codec_options import CodecOptions
from dateutil import tz

JAKARTA_TIMEZONE = tz.gettz('Asia/Jakarta')


class ResponseHandler:

    def __init__(self, holidays_collection, message_templater):
        self.holidays_collection = holidays_collection
        self.templater = message_templater

    def year(self, year=None):
        year = datetime.now().year if year is None else int(year)

        yearly_holidays = self.holidays_collection.find({
            'foremost_date': {
                '$gte': datetime(year, 1, 1, tzinfo=JAKARTA_TIMEZONE),
                '$lt': datetime(year + 1, 1, 1, tzinfo=JAKARTA_TIMEZONE)
            }
        })

        message = "Berikut adalah hari libur untuk tahun {year}\n".format_map({'year': year})

        current_month = -1
        for holiday in yearly_holidays:
            foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)

            header_active = False
            if current_month != foremost_date.month:
                header_active = True
                current_month = foremost_date.month

            message += self.templater.holiday_only_templating(holiday, header_active)

        return message

    def recommendation(self):

        current_time = datetime.now().astimezone(tz=JAKARTA_TIMEZONE)
        max_incoming_time = current_time + timedelta(days=91)

        yearly_holidays = self.holidays_collection.find({
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

            message += self.templater.recommendation_templating(holiday, header_active)

        return message

    def incoming(self):

        current_time = datetime.now().astimezone(tz=JAKARTA_TIMEZONE)
        max_incoming_time = current_time + timedelta(days=91)

        yearly_holidays = self.holidays_collection.find({
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

            message += self.templater.holiday_only_templating(holiday, header_active)

        message += '\nUntuk melihat rekomendasi cuti, silakan pilih "Rekomendasi cuti"\n'
        return message

    def help(self):
        return """
Untuk menjaga keseimbangan kerja dan liburan, bot ini dibuat sebagai referensi untuk pengambilan cuti anda. 

Silakan dicoba.
Kritik dan saran silakan hubungi @swallowstalker ya.
"""
