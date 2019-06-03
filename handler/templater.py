from dateutil import tz
from datetime import datetime, timedelta

import humanize

JAKARTA_TIMEZONE = tz.gettz('Asia/Jakarta')

MONTH_HEADER_TEMPLATE = "----------------\n" \
                        "<b>{month_name}</b>\n"
HOLIDAY_ONLY_TEMPLATE = "({estimation})\n" \
                        "⚫ {holiday_date_string} (<b>{description}</b>)\n"

RECOMMENDATION_TEMPLATE = HOLIDAY_ONLY_TEMPLATE + "{recommendations}\n"
LEAVE_RECOMMENDATION_TEMPLATE = "Rekomendasi cuti ({total_leave} hari cuti, {total_holiday_plus_leave} hari libur)\n" \
                                "{leave_recommendation_date_list}" \
                                "Liburan dari {holiday_plus_leave_start} - {holiday_plus_leave_end}\n"


class TemplateGenerator:
    def holiday_only_templating(self, holiday, header_active=False):
        foremost_date = holiday['foremost_date'].astimezone(JAKARTA_TIMEZONE)
        message = ''
        if header_active:
            message += MONTH_HEADER_TEMPLATE.format_map({'month_name': foremost_date.strftime('%B %Y')})

        message += HOLIDAY_ONLY_TEMPLATE.format_map({
            'estimation': self._estimate(holiday['foremost_date']),
            'holiday_date_string': self._holiday_range_string(holiday),
            'description': holiday['description']
        })

        return message

    def recommendation_templating(self, holiday, header_active=False):
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
            total_holiday_plus_leave = holiday_streak_delta + timedelta(days=1)

            leave_recommendation_date_list = ''
            for leave in holiday['leave_recommendation']:
                leave_recommendation_date_list += "☉ " + leave.astimezone(JAKARTA_TIMEZONE).strftime('%A %d %b') + "\n"

            recommendation_submessage = LEAVE_RECOMMENDATION_TEMPLATE.format_map({
                'total_leave': total_leave,
                'total_holiday_plus_leave': total_holiday_plus_leave.days,
                'leave_recommendation_date_list': leave_recommendation_date_list,
                'holiday_plus_leave_start': holiday_streak_start.strftime('%A %d %b'),
                'holiday_plus_leave_end': holiday_streak_end.strftime('%A %d %b')
            })

        else:
            recommendation_submessage = 'Tidak ada rekomendasi cuti\n\n'

        message += RECOMMENDATION_TEMPLATE.format_map({
            'estimation': self._estimate(holiday['foremost_date']),
            'holiday_date_string': self._holiday_range_string(holiday),
            'description': holiday['description'],
            'recommendations': recommendation_submessage
        })
        return message

    def _holiday_range_string(self, holiday):
        holiday_start = holiday["date_list"][0].astimezone(JAKARTA_TIMEZONE).strftime('%A %d %b')
        holiday_end = holiday["date_list"][-1].astimezone(JAKARTA_TIMEZONE).strftime('%A %d %b')

        holiday_date_string = holiday_start
        holiday_date_string += " - " + holiday_end if holiday_start != holiday_end else ""
        return holiday_date_string

    def _estimate(self, target_datetime=None):
        target_datetime = datetime.now(tz=JAKARTA_TIMEZONE) if target_datetime is None else target_datetime
        diff = target_datetime - datetime.now(tz=JAKARTA_TIMEZONE)
        return humanize.naturaltime(diff)
