from typing import Dict, List, Type
from abc import ABC, abstractmethod
import json

from aiohttp import ClientSession
from requests.exceptions import HTTPError

from deliveryAPI.models import USER_AGENT
from deliveryAPI.cache.LocationCache import UELocationCache


class BaseFoodModel(ABC):

    def __init__(self, postcode: str):
        self._postcode = postcode

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def canDeliver(self) -> bool:
        pass


class IndependentDeliveryModel(BaseFoodModel, ABC):

    def __init__(self, postcode):
        super().__init__(postcode)
        self._session = ClientSession()


class PizzaHut(IndependentDeliveryModel):

    @property
    def name(self):
        return "Pizza Hut"

    async def canDeliver(self):
        try:
            locations = await self._getLocations()
            canDeliver = bool(locations)
            return canDeliver
        finally:
            await self._session.close()

    async def _getLocations(self) -> Dict:
        requestParams = {
            "postcode": self._postcode
        }
        response = await self._session.get(
            "https://api.pizzahut.io/v1/huts",
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            params=requestParams
        )
        response.raise_for_status()
        locations = await response.json()
        return locations


class Dominos(IndependentDeliveryModel):

    @property
    def name(self):
        return "Dominos"

    async def canDeliver(self):
        try:
            locations = await self._getLocations()
            canDeliver = self._parseLocations(locations)
            return canDeliver
        finally:
            await self._session.close()

    async def _getLocations(self) -> Dict:
        requestParams = {
            "locationToken": f'UK-PC:{{"postCode":"{self._postcode}"}}',
            "radius": "30",
            "limit": "10"
        }
        response = await self._session.get(
            "https://www.dominos.co.uk/api/stores/v1/stores",
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            params=requestParams
        )
        try:
            response.raise_for_status()
        except HTTPError as httpError:
            if httpError.response.status_code == 404:
                # no locations exist
                return {}
            raise
        return await response.json()

    def _parseLocations(self, locations: Dict) -> bool:
        try:
            localStore = locations["data"]["localStore"]
            return localStore["catchmentServiceability"]["reason"] == "None"
        except KeyError:
            return False


class UberEatsSession(ClientSession):

    X_CSRF_TOKEN: str = "x"  # Seems to always be "x" for now, luckily

    def __init__(self, postcode):
        super().__init__()
        self.postcode = postcode

    def setCookie(self, key, value):
        self.cookie_jar.update_cookies(
            {key: value}
        )

    async def post(self, *args, headers: Dict = None, **kwargs):
        headers = {} if not headers else headers
        headers["x-csrf-token"] = self.X_CSRF_TOKEN
        return await super().post(*args, headers=headers, **kwargs)


class UberEats(BaseFoodModel, ABC):

    def __init__(self, postcode):
        super().__init__(postcode)
        self._session = UberEatsSession(postcode)
        self._addressInformation = None
        self._locationInformation = None

    @property
    @abstractmethod
    def searchParameter(self) -> str:
        pass

    @property
    def name(self):
        return "Uber Eats"

    async def canDeliver(self):
        try:
            if await self._setAddressInformation() is False:
                return False

            locations = await self._findLocations()
            canDeliver = self._parseResponse(locations)
            return canDeliver
        finally:
            await self._session.close()

    async def _findLocations(self) -> Dict:
        requestData = {
            "userQuery": self.searchParameter,
            "date": "",
            "startTime": 0,
            "endTime": 0,
            "vertical": "ALL",
        }
        response = await self._session.post(
            "https://www.ubereats.com/api/getSearchSuggestionsV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            data=requestData
        )
        response.raise_for_status()

        return await response.json()

    async def _setAddressInformation(self):
        await self._getAddressInformation()
        if not self._addressInformation:
            return False

        if not self._locationInformation:
            await self._setLocationInformation()

        self._session.setCookie("uev2.loc", json.dumps(self._locationInformation))

    async def _setLocationInformation(self):
        response = await self._session.post(
            "https://www.ubereats.com/_p/api/getDeliveryLocationV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            json={
                "placeId": self._addressInformation["id"],
                "provider": "google_places",
                "source": "manual_auto_complete"
            }
        )
        jsonResponse = await response.json()
        self._locationInformation = jsonResponse["data"]
        UELocationCache.setCacheLocation(self._postcode, self._locationInformation)

    async def _getAddressInformation(self):
        cachedLocation = UELocationCache.getCacheLocation(self._postcode)
        if cachedLocation:
            self._addressInformation = True
            self._locationInformation = cachedLocation
            return

        await self._getAddressInformationFromUE()

    async def _getAddressInformationFromUE(self):
        requestParams = {
            "query": self._postcode,
        }
        response = await self._session.post(
            "https://www.ubereats.com/api/getLocationAutocompleteV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            data=requestParams
        )
        response.raise_for_status()
        jsonResponse = await response.json()

        if jsonResponse["data"]:
            self._addressInformation = jsonResponse["data"][0]

    def _parseResponse(self, response) -> bool:
        responseData = response["data"]
        for responseItem in responseData:
            if (
                responseItem["type"] == "store" and
                self.searchParameter.lower() in responseItem["store"]["title"].lower()
            ):
                return True
        return False


class McDonalds(UberEats):

    @property
    def name(self):
        return f"{super().name} McDonalds"

    @property
    def searchParameter(self):
        return "mcdonald"


class KFC(UberEats):

    @property
    def name(self):
        return f"{super().name} KFC"

    @property
    def searchParameter(self):
        return "kfc"


class BurgerKing(UberEats):

    @property
    def name(self):
        return f"{super().name} Burger King"

    @property
    def searchParameter(self):
        return "burger king"


foodItems: List[Type[BaseFoodModel]] = [
    PizzaHut,
    Dominos,
    McDonalds,
    KFC,
    BurgerKing
]
