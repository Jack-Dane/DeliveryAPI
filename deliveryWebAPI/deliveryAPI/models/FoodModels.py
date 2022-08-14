
from typing import Dict, List, Type
from abc import ABC, abstractmethod
import json

import requests
from requests.exceptions import HTTPError

from deliveryAPI.models import USER_AGENT


class BaseFoodModel(ABC):

    def __init__(self, postcode: str):
        self._postcode = postcode

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def canDeliver(self) -> bool:
        pass


class IndependentDeliveryModel(BaseFoodModel, ABC):

    def __init__(self, postcode):
        super().__init__(postcode)
        self._session = requests.Session()


class PizzaHut(IndependentDeliveryModel):

    @property
    def name(self):
        return "Pizza Hut"

    def canDeliver(self):
        locations = self._getLocations()
        canDeliver = bool(locations)
        return canDeliver

    def _getLocations(self) -> Dict:
        requestParams = {
            "postcode": self._postcode
        }
        response = self._session.get(
            "https://api.pizzahut.io/v1/huts",
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            params=requestParams
        )
        response.raise_for_status()
        return response.json()


class Dominos(IndependentDeliveryModel):

    @property
    def name(self):
        return "Dominos"

    def canDeliver(self):
        locations = self._getLocations()
        canDeliver = self._parseLocations(locations)
        return canDeliver

    def _getLocations(self) -> Dict:
        requestParams = {
            "locationToken": f'UK-PC:{{"postCode":"{self._postcode}"}}',
            "radius": "30",
            "limit": "10"
        }
        response = self._session.get(
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
        return response.json()

    def _parseLocations(self, locations: Dict) -> bool:
        try:
            localStore = locations["data"]["localStore"]
            return localStore["catchmentServiceability"]["reason"] == "None"
        except KeyError:
            return False


class UberEatsSession(requests.Session):

    X_CSRF_TOKEN: str = "x"  # Seems to always be "x" for now, luckily

    def __init__(self):
        super().__init__()
        self.postcode = None

    def validSession(self, postcode: str) -> bool:
        if self.postcode != postcode:
            return False

        if postcode not in self.cookies.get("uev2.loc", ""):
            return False
        return True

    def post(self, *args, headers: Dict = None, **kwargs):
        headers = {} if not headers else headers
        headers["x-csrf-token"] = self.X_CSRF_TOKEN
        return super().post(*args, headers=headers, **kwargs)


class UberEats(BaseFoodModel, ABC):

    SESSION: UberEatsSession = UberEatsSession()

    def __init__(self, postcode):
        super().__init__(postcode)
        self._postcode = postcode
        if not self.SESSION.postcode:
            self.SESSION.postcode = postcode
        self._addressInformation = None

    @property
    @abstractmethod
    def searchParameter(self) -> str:
        pass

    @property
    def name(self):
        return "Uber Eats"

    def canDeliver(self):
        if not self._validSession():
            self._getAddressInformation()
            if not self._addressInformation:
                return False

            self._setAddressInformation()

        locations = self._findLocations()
        canDeliver = self._parseResponse(locations)
        return canDeliver

    def _validSession(self) -> bool:
        if UberEats.SESSION.validSession(self._postcode):
            return True
        UberEats.SESSION = UberEatsSession()
        UberEats.SESSION.postcode = self._postcode
        return False

    def _findLocations(self) -> Dict:
        requestData = {
            "userQuery": self.searchParameter,
            "date": "",
            "startTime": 0,
            "endTime": 0,
            "vertical": "ALL",
        }
        response = self.SESSION.post(
            "https://www.ubereats.com/api/getSearchSuggestionsV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            data=requestData
        )
        response.raise_for_status()
        return response.json()

    def _getAddressInformation(self):
        requestParams = {
            "query": self._postcode,
        }
        response = self.SESSION.post(
            "https://www.ubereats.com/api/getLocationAutocompleteV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            data=requestParams
        )
        response.raise_for_status()
        if response.json()["data"]:
            self._addressInformation = response.json()["data"][0]

    def _setAddressInformation(self):
        response = self.SESSION.post(
            "https://www.ubereats.com/api/getLocationDetailsV1?localeCode=gb",
            headers={"User-Agent": USER_AGENT},
            json=self._addressInformation
        )
        self.SESSION.cookies.set("uev2.loc", json.dumps(response.json()["data"]))

    def _parseResponse(self, response) -> bool:
        responseData = response["data"]
        for responseItem in responseData:
            if responseItem["type"] == "store" and self.searchParameter.lower() in responseItem["store"]["title"].lower():
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
