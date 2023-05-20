
from unittest import TestCase
from unittest.mock import patch

from deliveryAPI.api.api import foodDeliveryData

MODULE_PATH = "deliveryAPI.api.api."


class BaseExampleFoodItem:

    def __init__(self, postcode):
        self._postcode = postcode


class ExampleFoodItem1(BaseExampleFoodItem):

    @property
    def name(self):
        return "Example Food Item 1"

    def canDeliver(self):
        return True


class ExampleFoodItem2(BaseExampleFoodItem):

    @property
    def name(self):
        return "Example Food Item 2"

    def canDeliver(self):
        return False


@patch(MODULE_PATH + "foodItems", [ExampleFoodItem1, ExampleFoodItem2])
class test_foodDeliveryData(TestCase):

    def test_ok(self):
        response = foodDeliveryData("ABCD 1EF")

        self.assertEqual(
            {
                "Example Food Item 1": True,
                "Example Food Item 2": False
            },
            response
        )
