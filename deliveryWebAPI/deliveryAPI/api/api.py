from typing import Type, Dict

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


@app.get("/delivery/food/{postcode}")
def foodDeliveryData(postcode: str):
    response = {}
    for foodItem in foodItems:
        foodItemInstance = foodItem(postcode)
        response[foodItemInstance.name] = foodItemInstance.canDeliver()
    return response


@app.get("/delivery/food/pizzahut/{postcode}")
def foodDeliveryDataPizzaHut(postcode: str):
    return getResponseData(PizzaHut, postcode)


@app.get("/delivery/food/dominos/{postcode}")
def foodDeliveryDataDominos(postcode: str):
    return getResponseData(Dominos, postcode)


@app.get("/delivery/food/mcdonalds/{postcode}")
def foodDeliveryDataMcdonalds(postcode: str):
    return getResponseData(McDonalds, postcode)


@app.get("/delivery/food/kfc/{postcode}")
def foodDeliveryDataKFC(postcode: str):
    return getResponseData(KFC, postcode)


@app.get("/delivery/food/burgerking/{postcode}")
def foodDeliveryDataBurgerKing(postcode: str):
    return getResponseData(BurgerKing, postcode)
