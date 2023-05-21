from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, call, AsyncMock, AsyncMagicMixin

from aiohttp import ClientSession
from requests.exceptions import HTTPError

from deliveryAPI.models.FoodModels import (
    PizzaHut, Dominos, UberEatsSession, UberEats, USER_AGENT
)

MODULE_PATH = "deliveryAPI.models.FoodModels."


@patch(MODULE_PATH + "ClientSession", return_value=AsyncMock())
class Test_PizzaHut_canDeliver(IsolatedAsyncioTestCase):

    async def test_valid_locations(self, ClientSession_):
        self.pizzaHut = PizzaHut("ABCD 1EF")
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
        response = MagicMock(response_status=200)
        coroutineResponse = AsyncMock(return_value=response)
        response.json = AsyncMock(return_value=jsonResponse)
        ClientSession_.return_value.get = coroutineResponse

        canDeliver = await self.pizzaHut.canDeliver()

        self.assertTrue(canDeliver)

    async def test_no_locations(self, ClientSession_):
        self.pizzaHut = PizzaHut("ABCD 1EF")
        response = MagicMock(response_status=200)
        coroutineResponse = AsyncMock(return_value=response)
        response.json = AsyncMock(return_value=[])
        ClientSession_.return_value.get = coroutineResponse

        canDeliver = await self.pizzaHut.canDeliver()

        self.assertFalse(canDeliver)


@patch(MODULE_PATH + "ClientSession", return_value=AsyncMock())
class Test_Dominos_canDeliver(IsolatedAsyncioTestCase):

    async def test_valid_locations(self, ClientSession_):
        self.dominos = Dominos("ABCD 1EF")
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
        response = MagicMock(response_status=200)
        coroutineResponse = AsyncMock(return_value=response)
        response.json = AsyncMock(return_value=jsonResponse)
        ClientSession_.return_value.get = coroutineResponse

        canDeliver = await self.dominos.canDeliver()

        self.assertTrue(canDeliver)

    async def test_no_locations(self, ClientSession_):
        self.dominos = Dominos("ABCD 1EF")
        response = MagicMock()
        response.raise_for_status.side_effect = HTTPError(
            response=MagicMock(status_code=404)
        )
        coroutineResponse = AsyncMock(return_value=response)
        ClientSession_.return_value.get = coroutineResponse

        canDeliver = await self.dominos.canDeliver()

        self.assertFalse(canDeliver)

    async def test_no_local_locations(self, ClientSession_):
        self.dominos = Dominos("ABCD 1EF")
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
        response = MagicMock(response_status=200)
        response.json = AsyncMock(return_value=jsonResponse)
        coroutineResponse = AsyncMock(return_value=response)
        ClientSession_.return_value.get = coroutineResponse

        canDeliver = await self.dominos.canDeliver()

        self.assertFalse(canDeliver)

    async def test_local_store_does_not_deliver(self, ClientSession_):
        self.dominos = Dominos("ABCD 1EF")
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
        response = MagicMock(response_status=200)
        response.json = AsyncMock(return_value=jsonResponse)
        ClientSession_.return_value.get = AsyncMock(return_value=response)

        canDeliver = await self.dominos.canDeliver()

        self.assertFalse(canDeliver)


@patch.object(ClientSession, "__init__")
class Test_UberEatsSession_post(IsolatedAsyncioTestCase):

    async def test_passed_headers(self, _ClientSession):
        session = UberEatsSession("ABCD 1EF")

        with patch.object(ClientSession, "post", AsyncMock()) as postMock:
            await session.post(
                "https://www.ubereats.com",
                headers={"User-Agent": "UA"}
            )

        postMock.assert_called_once_with(
            "https://www.ubereats.com",
            headers={"User-Agent": "UA", "x-csrf-token": UberEatsSession.X_CSRF_TOKEN}
        )

    async def test_no_passed_headers(self, _ClientSession):
        session = UberEatsSession("ABCD 1EF")

        with patch.object(ClientSession, "post", AsyncMock()) as postMock:
            await session.post(
                "https://www.ubereats.com"
            )

        postMock.assert_called_once_with(
            "https://www.ubereats.com",
            headers={"x-csrf-token": UberEatsSession.X_CSRF_TOKEN}
        )


class UberEatsSubclassTest(UberEats):

    @property
    def searchParameter(self):
        return "Test"


@patch(MODULE_PATH + "UELocationCache")
@patch(MODULE_PATH + "UberEatsSession", return_value=AsyncMock())
class Test_UberEats_canDeliver(IsolatedAsyncioTestCase):

    async def test_ok(self, UberEatsSession_, UELocationCache):
        UELocationCache.getCacheLocation.return_value = None
        getAddressInfoResponse = MagicMock()
        getAddressInfoResponse.json = AsyncMock(return_value={
            "data": [
                {
                    "id": "abc123"
                }
            ]
        })
        setAddressInfoResponse = MagicMock()
        setAddressInfoResponse.json = AsyncMock(return_value={
            "data": [
                "addressData"
            ]
        })
        locationResponse = MagicMock()
        locationResponse.json = AsyncMock(return_value={
            "data": [
                {
                    "type": "store",
                    "store": {
                        "title": "ABC TEST ABC"
                    }
                }
            ]
        })
        UberEatsSession_.return_value.post = AsyncMock(
            side_effect=[getAddressInfoResponse, setAddressInfoResponse, locationResponse]
        )
        UberEatsSession_.return_value.setCookie = MagicMock()
        uberEats = UberEatsSubclassTest("ABCD 1EF")

        canDeliver = await uberEats.canDeliver()

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
            UberEatsSession_.return_value.post.mock_calls
        )
        UberEatsSession_.return_value.setCookie.assert_called_once_with("uev2.loc", '["addressData"]')
        UELocationCache.setCacheLocation.assert_called_once_with(
            "ABCD 1EF", setAddressInfoResponse.json.return_value["data"]
        )

    async def test_cached_location(self, UberEatsSession_, UELocationCache):
        UELocationCache.getCacheLocation.return_value = {
            "cached": "location"
        }
        locationResponse = MagicMock()
        locationResponse.json = AsyncMock(return_value={
            "data": [
                {
                    "type": "store",
                    "store": {
                        "title": "ABC TEST ABC"
                    }
                }
            ]
        })
        UberEatsSession_.return_value.post = AsyncMock(return_value=locationResponse)
        UberEatsSession_.return_value.setCookie = MagicMock()
        uberEats = UberEatsSubclassTest("ABCD 1EF")

        canDeliver = await uberEats.canDeliver()

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
            UberEatsSession_.return_value.post.mock_calls
        )
        uberEats._session.setCookie.assert_called_once_with("uev2.loc", '{"cached": "location"}')
        UELocationCache.setCacheLocation.assert_not_called()

    async def test_no_location(self, UberEatsSession_, UELocationCache):
        UELocationCache.getCacheLocation.return_value = None
        response = MagicMock()
        UberEatsSession_.return_value.post = AsyncMock(return_value=response)
        response.json = AsyncMock(return_value={
            "data": []
        })
        uberEats = UberEatsSubclassTest("ABCD 1EF")

        canDeliver = await uberEats.canDeliver()

        self.assertFalse(canDeliver)
        self.assertEqual(0, UELocationCache.setCacheLocation.call_count)

    async def test_no_valid_stores(self, UberEatsSession_, UELocationCache):
        UELocationCache.getCacheLocation.return_value = None
        response = MagicMock()
        UberEatsSession_.return_value.post = AsyncMock(return_value=response)
        UberEatsSession_.return_value.setCookie = MagicMock()
        response.json = AsyncMock(return_value={
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
        })
        uberEats = UberEatsSubclassTest("ABCD 1EF")

        canDeliver = await uberEats.canDeliver()

        self.assertFalse(canDeliver)
        self.assertEqual(1, UELocationCache.setCacheLocation.call_count)
