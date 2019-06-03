import unittest
from datetime import datetime
from dateutil import tz

from handler.templater import TemplateGenerator

JAKARTA_TIMEZONE = tz.gettz('Asia/Jakarta')


class TestYearHandlerWithParam(unittest.TestCase):

    INCOMING_HOLIDAY = [
        {
            "description": "Dummy Holiday",
            "date_list": [datetime(2018, 1, 4).astimezone(JAKARTA_TIMEZONE),
                          datetime(2018, 1, 5).astimezone(JAKARTA_TIMEZONE)],
            "holiday_streak": {
                "start": datetime(2018, 1, 4).astimezone(JAKARTA_TIMEZONE),
                "end": datetime(2018, 1, 4).astimezone(JAKARTA_TIMEZONE)
            },
            "leave_recommendation": [datetime(2018, 1, 5).astimezone(JAKARTA_TIMEZONE),
                                     datetime(2018, 1, 8).astimezone(JAKARTA_TIMEZONE)],
            "foremost_date": datetime(2018, 1, 4).astimezone(JAKARTA_TIMEZONE)
        }
    ]

    def test_holiday_only(self):
        generator = TemplateGenerator()
        result = generator.holiday_only_templating(self.INCOMING_HOLIDAY[0]).splitlines()

        # test second line only as it is static
        self.assertEqual(result[1], "⚫ Thursday 04 Jan - Friday 05 Jan (<b>Dummy Holiday</b>)")


if __name__ == "__main__":
    unittest.main()