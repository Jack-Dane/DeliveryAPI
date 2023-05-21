from typing import Type, Dict, Union
import time

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deliveryAPI.models.FoodModels import (
    BaseFoodModel, foodItems, PizzaHut, Dominos, McDonalds, KFC, BurgerKing
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def getResponseData(foodItem: Type[BaseFoodModel], postcode: str) -> Dict:
    foodItemInstance = foodItem(postcode)
    return {foodItemInstance.name: await foodItemInstance.canDeliver()}


@app.get("/delivery/food")
async def foodDeliveryData(postcode: Union[str, None]):
    response = {}
    for foodItem in foodItems:
        foodItemInstance = foodItem(postcode)
        foodItemTask = asyncio.create_task(foodItemInstance.canDeliver())
        response[foodItemInstance.name] = foodItemTask

    for name, task in response.items():
        response[name] = await task

    return response


@app.get("/delivery/food/pizzahut")
async def foodDeliveryDataPizzaHut(postcode: Union[str, None]):
    return await getResponseData(PizzaHut, postcode)


@app.get("/delivery/food/dominos")
async def foodDeliveryDataDominos(postcode: Union[str, None]):
    return await getResponseData(Dominos, postcode)


@app.get("/delivery/food/mcdonalds")
async def foodDeliveryDataMcdonalds(postcode: Union[str, None]):
    return await getResponseData(McDonalds, postcode)


@app.get("/delivery/food/kfc")
async def foodDeliveryDataKFC(postcode: Union[str, None]):
    return await getResponseData(KFC, postcode)


@app.get("/delivery/food/burgerking")
async def foodDeliveryDataBurgerKing(postcode: Union[str, None]):
    return await getResponseData(BurgerKing, postcode)
