from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from fastapi import HTTPException

from deliveryAPI.api.api import (
    foodDeliveryData, getDeliveryServiceFromEndpoint, PizzaHut
)

MODULE_PATH = "deliveryAPI.api.api."


class BaseExampleFoodItem:

    def __init__(self, postcode):
        self._postcode = postcode


class ExampleFoodItem1(BaseExampleFoodItem):

    @property
    def name(self):
        return "Example Food Item 1"

    async def canDeliver(self):
        return True


class ExampleFoodItem2(BaseExampleFoodItem):

    @property
    def name(self):
        return "Example Food Item 2"

    async def canDeliver(self):
        return False


@patch(MODULE_PATH + "foodItems", [ExampleFoodItem1, ExampleFoodItem2])
class Test_foodDeliveryData(IsolatedAsyncioTestCase):

    async def test_ok(self):
        response = await foodDeliveryData("ABCD 1EF")

        self.assertEqual(
            {
                "Example Food Item 1": {
                    "can_deliver": True,
                },
                "Example Food Item 2": {
                    "can_deliver": False
                }
            },
            response
        )


class Test_getDeliveryServiceFromEndpoint(IsolatedAsyncioTestCase):

    async def test_backend_found(self):
        deliveryService = await getDeliveryServiceFromEndpoint("pizzahut")

        self.assertEqual(PizzaHut, deliveryService)

    async def test_no_backend(self):
        with self.assertRaises(HTTPException) as httpError:
            await getDeliveryServiceFromEndpoint("notfound")

        self.assertEqual(404, httpError.exception.status_code)
        self.assertEqual(
            "Could not find delivery service backend for notfound",
            httpError.exception.detail
        )
