from unittest import TestCase
from unittest.mock import patch, MagicMock

from deliveryAPI.cache.LocationCache import UE_LocationCache


MODULE_PATH = "deliveryAPI.cache.LocationCache."


@patch(MODULE_PATH + "dbm")
@patch(MODULE_PATH + "time")
class Test_locationCache_getCacheLocation(TestCase):

    def test_valid_cache(self, time_, dbm):
        time_.time.return_value = 604800
        dbCache = MagicMock()
        dbCache.get.return_value = '{"example": "data", "create_date": 0}'
        dbm.open.return_value.__enter__.return_value = dbCache

        location = UE_LocationCache.getCacheLocation("AB12ABC")

        self.assertEqual(
            {
                "example": "data"
            },
            location
        )

    def test_no_postcode_cache(self, _time, dbm):
        dbCache = MagicMock()
        dbCache.get.return_value = None
        dbm.open.return_value.__enter__.return_value = dbCache

        location = UE_LocationCache.getCacheLocation("AB12ABC")

        self.assertIsNone(location)

    def test_expired(self, time_, dbm):
        time_.time.return_value = 604801
        dbCache = MagicMock()
        dbCache.get.return_value = '{"example": "data", "create_date": 0}'
        dbm.open.return_value.__enter__.return_value = dbCache

        location = UE_LocationCache.getCacheLocation("AB12ABC")

        self.assertIsNone(location)


@patch(MODULE_PATH + "dbm")
@patch(MODULE_PATH + "time")
class Test_locationCache_setCacheLocation(TestCase):

    def test_ok(self, time_, dbm):
        time_.time.return_value = 1234
        dbm.open.return_value.__enter__.return_value = {}

        UE_LocationCache.setCacheLocation(
            "AB12ABC", {"example": "data"}
        )

        self.assertEqual(
            '{"example": "data", "create_date": 1234}',
            dbm.open.return_value.__enter__.return_value["AB12ABC"]
        )
