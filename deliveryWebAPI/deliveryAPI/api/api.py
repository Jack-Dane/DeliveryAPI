from typing import Type, Dict, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deliveryAPI.models.FoodModels import (
    BaseFoodModel, foodItems, PizzaHut, Dominos, McDonalds, KFC, BurgerKing
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def getResponseData(foodItem: Type[BaseFoodModel], postcode: str) -> Dict:
    foodItemInstance = foodItem(postcode)
    return {foodItemInstance.name: foodItemInstance.canDeliver()}


@app.get("/delivery/food")
def foodDeliveryData(postcode: Union[str, None]):
    response = {}
    for foodItem in foodItems:
        foodItemInstance = foodItem(postcode)
        response[foodItemInstance.name] = foodItemInstance.canDeliver()
    return response


@app.get("/delivery/food/pizzahut")
def foodDeliveryDataPizzaHut(postcode: Union[str, None]):
    return getResponseData(PizzaHut, postcode)


@app.get("/delivery/food/dominos")
def foodDeliveryDataDominos(postcode: Union[str, None]):
    return getResponseData(Dominos, postcode)


@app.get("/delivery/food/mcdonalds")
def foodDeliveryDataMcdonalds(postcode: Union[str, None]):
    return getResponseData(McDonalds, postcode)


@app.get("/delivery/food/kfc")
def foodDeliveryDataKFC(postcode: Union[str, None]):
    return getResponseData(KFC, postcode)


@app.get("/delivery/food/burgerking")
def foodDeliveryDataBurgerKing(postcode: Union[str, None]):
    return getResponseData(BurgerKing, postcode)
