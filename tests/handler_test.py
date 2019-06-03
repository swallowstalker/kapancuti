import unittest
from datetime import datetime

from handler.handler import ResponseHandler


class TestYearHandlerWithParam(unittest.TestCase):

    def test_empty(self):
        handler = ResponseHandler(DummyCollection("empty"), DummyTemplater())
        result = handler.year(2017)

        expected = "Berikut adalah hari libur untuk tahun 2017\n"
        self.assertEqual(result, expected, "year not match")

    def test_incoming(self):
        handler = ResponseHandler(DummyCollection("incoming"), DummyTemplater())
        result = handler.year(2017)

        expected = "Berikut adalah hari libur untuk tahun 2017\n"
        expected += "Holiday only: Dummy Holiday: 2018-01-04\n"
        self.assertEqual(result, expected, "year not match")


class TestYearHandlerWithoutParam(unittest.TestCase):
    def test_empty(self):
        handler = ResponseHandler(DummyCollection("empty"), DummyTemplater())
        result = handler.year()

        expected = "Berikut adalah hari libur untuk tahun {year}\n".format_map({'year': datetime.now().year})
        self.assertEqual(result, expected, "year not match")

    def test_incoming(self):
        handler = ResponseHandler(DummyCollection("incoming"), DummyTemplater())
        result = handler.year()

        expected = "Berikut adalah hari libur untuk tahun {year}\n".format_map({'year': datetime.now().year})
        expected += "Holiday only: Dummy Holiday: 2018-01-04\n"
        self.assertEqual(result, expected, "year not match")


class TestRecommendation(unittest.TestCase):
    def test_empty(self):
        handler = ResponseHandler(DummyCollection("empty"), DummyTemplater())
        result = handler.recommendation()
        expected = "Berikut adalah hari libur dan rekomendasi cuti untuk 3 bulan mendatang\n"
        self.assertEqual(result, expected, "recommendation not match")

    def test_incoming(self):
        handler = ResponseHandler(DummyCollection("incoming"), DummyTemplater())
        result = handler.recommendation()
        expected = "Berikut adalah hari libur dan rekomendasi cuti untuk 3 bulan mendatang\n"
        expected += "With recommendation: Dummy Holiday: 2018-01-04\n"
        self.assertEqual(result, expected, "recommendation not match")


class TestIncoming(unittest.TestCase):
    def test_empty(self):
        handler = ResponseHandler(DummyCollection("empty"), DummyTemplater())
        result = handler.incoming()
        expected = "Berikut adalah hari libur untuk 3 bulan yang akan datang\n"
        expected += '\nUntuk melihat rekomendasi cuti, silakan pilih "Rekomendasi cuti"\n'
        self.assertEqual(result, expected, "incoming not match")

    def test_incoming(self):
        handler = ResponseHandler(DummyCollection("incoming"), DummyTemplater())
        result = handler.incoming()
        expected = "Berikut adalah hari libur untuk 3 bulan yang akan datang\n"
        expected += "Holiday only: Dummy Holiday: 2018-01-04\n"
        expected += '\nUntuk melihat rekomendasi cuti, silakan pilih "Rekomendasi cuti"\n'
        self.assertEqual(result, expected, "incoming not match")


class DummyCollection:

    EMPTY_HOLIDAY = []
    INCOMING_HOLIDAY = [
        {
            "description": "Dummy Holiday",
            "date_list": [datetime(2018, 1, 4), datetime(2018, 1, 5)],
            "holiday_streak": {
                "start": datetime(2018, 1, 4),
                "end": datetime(2018, 1, 4)
            },
            "leave_recommendation": [datetime(2018, 1, 5), datetime(2018, 1, 8)],
            "foremost_date": datetime(2018, 1, 4)
        }
    ]

    def __init__(self, scenario_type):
        self.scenario = {
            "empty": self.EMPTY_HOLIDAY,
            "incoming": self.INCOMING_HOLIDAY
        }
        self.type = scenario_type

    def find(self, args):
        return self.scenario[self.type]

    def count(self):
        return len(self.scenario[self.type])


class DummyTemplater():
    def holiday_only_templating(self, holiday, header_active=False):
        return "Holiday only: {description}: {foremost_date}\n".format_map({
            "description": holiday["description"], "foremost_date": holiday["foremost_date"].strftime("%Y-%m-%d")})

    def recommendation_templating(self, holiday, header_active=False):
        return "With recommendation: {description}: {foremost_date}\n".format_map({
            "description": holiday["description"], "foremost_date": holiday["foremost_date"].strftime("%Y-%m-%d")})


if __name__ == "__main__":
    unittest.main()