from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from requests import Session
from requests.exceptions import HTTPError

from deliveryAPI.models.FoodModels import (
    PizzaHut, Dominos, UberEatsSession, UberEats, USER_AGENT
)

MODULE_PATH = "deliveryAPI.models.FoodModels."


@patch.object(Session, "get")
class Test_PizzaHut_canDeliver(TestCase):

    def setUp(self):
        self.pizzaHut = PizzaHut("ABCD 1EF")

    def test_valid_locations(self, Session_get):
        jsonResponse = [
            {
                "urn": "urn:yum:store:6244834e-b054-4cd2-bcb3-3f418bf2c6bc",
                "sector": "uk-1",
                "id": "501",
                "name": "Kingsbury",
                "address": {
                    "lines": [
                        "497 Kingsbury Road",
                        "Kingsbury",
                        "London"
                    ],
                    "postcode": "NW9 9ED"
                }
            },
        ]
        response = MagicMock()
        response.response_status = 200
        response.json.return_value = jsonResponse
        Session_get.return_value = response

        canDeliver = self.pizzaHut.canDeliver()

        self.assertTrue(canDeliver)

    def test_no_locations(self, Session_get):
        jsonResponse = []
        response = MagicMock(test="abc")
        response.response_status = 200
        response.json.return_value = jsonResponse
        Session_get.return_value = response

        canDeliver = self.pizzaHut.canDeliver()

        self.assertFalse(canDeliver)


@patch.object(Session, "get")
class Test_Dominos_canDeliver(TestCase):

    def setUp(self):
        self.dominos = Dominos("ABCD 1EF")

    def test_valid_locations(self, Session_get):
        jsonResponse = {
            'data': {
                'localStore': {
                    'id': '28146',
                    'name': 'Ashford',
                    'contacts': {
                        'phone': '01233 666600',
                        'customerConcernPhone': '01233 666600',
                        'customerConcernEmail': 'weissdominos@aol.com'
                    },
                    "catchmentServiceability": {
                        "reason": "None"
                    }
                }
            }
        }
        response = MagicMock()
        response.response_status = 200
        response.json.return_value = jsonResponse
        Session_get.return_value = response

        canDeliver = self.dominos.canDeliver()

        self.assertTrue(canDeliver)

    def test_no_locations(self, Session_get):
        response = MagicMock()
        response.raise_for_status.side_effect = HTTPError(
            response=MagicMock(status_code=404)
        )
        Session_get.return_value = response

        canDeliver = self.dominos.canDeliver()

        self.assertFalse(canDeliver)

    def test_no_local_locations(self, Session_get):
        jsonResponse = {
            'data': {
                'stores': {
                    'id': '28146',
                    'name': 'Ashford',
                    'contacts': {
                        'phone': '01233 666600',
                        'customerConcernPhone': '01233 666600',
                        'customerConcernEmail': 'weissdominos@aol.com'
                    },
                    "catchmentServiceability": {
                        "reason": "None"
                    }
                }
            }
        }
        response = MagicMock()
        response.response_status = 200
        response.json.return_value = jsonResponse
        Session_get.return_value = response

        canDeliver = self.dominos.canDeliver()

        self.assertFalse(canDeliver)

    def test_local_store_does_not_deliver(self, Session_get):
        jsonResponse = {
            'data': {
                'localStore': {
                    'id': '28146',
                    'name': 'Ashford',
                    'contacts': {
                        'phone': '01233 666600',
                        'customerConcernPhone': '01233 666600',
                        'customerConcernEmail': 'weissdominos@aol.com'
                    },
                    "catchmentServiceability": {
                        "reason": "TooFar"  # example, not actual response data
                    }
                }
            }
        }
        response = MagicMock()
        response.response_status = 200
        response.json.return_value = jsonResponse
        Session_get.return_value = response

        canDeliver = self.dominos.canDeliver()

        self.assertFalse(canDeliver)


@patch(MODULE_PATH + "requests")
class Test_UberEatsSession_validSession(TestCase):

    def test_valid_session(self, requests):
        session = UberEatsSession("ABCD 1EF")
        session.cookies.set("uev2.loc", "XYZ ABCD 1EF XYZ")

        isValidSession = session.validSession("ABCD 1EF")

        self.assertTrue(isValidSession)

    def test_no_cookie(self, requests):
        session = UberEatsSession("ABCD 1EF")

        isValidSession = session.validSession("ABCD 1EF")

        self.assertFalse(isValidSession)

    def test_different_postcode(self, requests):
        session = UberEatsSession("ABCD 1EF")
        session.cookies.set("uev2.loc", "XYZ ABCD 1EF XYZ")

        isValidSession = session.validSession("DCBA 1EF")

        self.assertFalse(isValidSession)


@patch(MODULE_PATH + "requests")
@patch.object(Session, "post")
class Test_UberEatsSession_post(TestCase):

    def test_passed_headers(self, Session_post, requests):
        session = UberEatsSession("ABCD 1EF")

        session.post(
            "https://www.ubereats.com",
            headers={"User-Agent": "UA"}
        )

        Session_post.assert_called_once_with(
            "https://www.ubereats.com",
            headers={"User-Agent": "UA", "x-csrf-token": UberEatsSession.X_CSRF_TOKEN}
        )

    def test_no_passed_headers(self, Session_post, rqeuests):
        session = UberEatsSession("ABCD 1EF")

        session.post(
            "https://www.ubereats.com"
        )

        Session_post.assert_called_once_with(
            "https://www.ubereats.com",
            headers={"x-csrf-token": UberEatsSession.X_CSRF_TOKEN}
        )


class UberEatsSubclassTest(UberEats):

    @property
    def searchParameter(self):
        return "Test"


@patch(MODULE_PATH + "requests")
@patch(MODULE_PATH + "UELocationCache")
class Test_UberEats_canDeliver(TestCase):

    def test_ok(self, UELocationCache, requests):
        UELocationCache.getCacheLocation.return_value = None
        uberSession = MagicMock()
        getAddressInfoResponse = MagicMock()
        getAddressInfoResponse.json.return_value = {
            "data": [
                {
                    "id": "abc123"
                }
            ]
        }
        setAddressInfoResponse = MagicMock()
        setAddressInfoResponse.json.return_value = {
            "data": [
                "addressData"
            ]
        }
        locationResponse = MagicMock()
        locationResponse.json.return_value = {
            "data": [
                {
                    "type": "store",
                    "store": {
                        "title": "ABC TEST ABC"
                    }
                }
            ]
        }
        uberSession.post.side_effect = [getAddressInfoResponse, setAddressInfoResponse, locationResponse]
        uberEats = UberEatsSubclassTest("ABCD 1EF")
        uberEats._session = uberSession

        canDeliver = uberEats.canDeliver()

        self.assertTrue(canDeliver)
        self.assertEqual(
            [
                call(
                    "https://www.ubereats.com/api/getLocationAutocompleteV1?localeCode=gb",
                    headers={"User-Agent": USER_AGENT},
                    data={"query": "ABCD 1EF"}
                ),
                call(
                    "https://www.ubereats.com/_p/api/getDeliveryLocationV1?localeCode=gb",
                    headers={"User-Agent": USER_AGENT},
                    json={
                        "placeId": "abc123",
                        "provider": "google_places",
                        "source": "manual_auto_complete"
                    }
                ),
                call(
                    "https://www.ubereats.com/api/getSearchSuggestionsV1?localeCode=gb",
                    headers={"User-Agent": USER_AGENT},
                    data={
                        "userQuery": "Test",
                        "date": "",
                        "startTime": 0,
                        "endTime": 0,
                        "vertical": "ALL",
                    }
                ),
            ],
            uberSession.post.mock_calls
        )
        uberSession.cookies.set.assert_called_once_with("uev2.loc", '["addressData"]')
        UELocationCache.setCacheLocation.assert_called_once_with(
            "ABCD 1EF", setAddressInfoResponse.json.return_value["data"]
        )

    def test_cached_location(self, UELocationCache, requests):
        UELocationCache.getCacheLocation.return_value = {
            "cached": "location"
        }
        uberSession = MagicMock()
        locationResponse = MagicMock()
        locationResponse.json.return_value = {
            "data": [
                {
                    "type": "store",
                    "store": {
                        "title": "ABC TEST ABC"
                    }
                }
            ]
        }
        uberSession.post.side_effect = [locationResponse]
        uberEats = UberEatsSubclassTest("ABCD 1EF")
        uberEats._session = uberSession

        canDeliver = uberEats.canDeliver()

        self.assertTrue(canDeliver)
        self.assertEqual(
            [
                call(
                    "https://www.ubereats.com/api/getSearchSuggestionsV1?localeCode=gb",
                    headers={"User-Agent": USER_AGENT},
                    data={
                        "userQuery": "Test",
                        "date": "",
                        "startTime": 0,
                        "endTime": 0,
                        "vertical": "ALL",
                    }
                ),
            ],
            uberSession.post.mock_calls
        )
        uberSession.cookies.set.assert_called_once_with("uev2.loc", '{"cached": "location"}')
        UELocationCache.setCacheLocation.assert_not_called()

    def test_no_location(self, UELocationCache, requests):
        UELocationCache.getCacheLocation.return_value = None
        uberSession = MagicMock()
        response = MagicMock()
        uberSession.post.return_value = response
        response.json.return_value = {
            "data": []
        }
        uberEats = UberEatsSubclassTest("ABCD 1EF")
        uberEats._session = uberSession

        canDeliver = uberEats.canDeliver()

        self.assertFalse(canDeliver)
        self.assertEqual(0, UELocationCache.setCacheLocation.call_count)

    def test_no_valid_stores(self, UELocationCache, requests):
        UELocationCache.getCacheLocation.return_value = None
        uberSession = MagicMock()
        response = MagicMock()
        uberSession.post.return_value = response
        response.json.return_value = {
            "data": [
                {
                    "id": "abc123",
                    "type": "store",
                    "store": {
                        "title": "ABC TE ST ABC"
                    }
                },
                {
                    "id": "abc234",
                    "type": "text",
                    "store": {
                        "title": "ABC TEST ABC"
                    }
                }
            ]
        }
        uberEats = UberEatsSubclassTest("ABCD 1EF")
        uberEats._session = uberSession

        canDeliver = uberEats.canDeliver()

        self.assertFalse(canDeliver)
        self.assertEqual(1, UELocationCache.setCacheLocation.call_count)
