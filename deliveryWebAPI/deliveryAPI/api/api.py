from typing import Type, Dict, Union

import asyncio
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from fastapi.middleware.cors import CORSMiddleware

from deliveryAPI.models.FoodModels import (
    BaseFoodModel, foodItems, PizzaHut, Dominos, McDonalds, KFC, BurgerKing
)
from deliveryAPI.api import schemas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


DELIVERY_SERVICE_ENDPOINT_MAPPING = {
    "pizzahut": PizzaHut,
    "dominos": Dominos,
    "mcdonalds": McDonalds,
    "kfc": KFC,
    "burgerking": BurgerKing
}


async def getDeliveryServiceFromEndpoint(endpoint: str) -> Type[BaseFoodModel]:
    try:
        return DELIVERY_SERVICE_ENDPOINT_MAPPING[endpoint]
    except KeyError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Could not find delivery service backend for {endpoint}"
        )


async def getResponseData(deliveryService: str, postcode: str) -> Dict:
    foodItem = await getDeliveryServiceFromEndpoint(deliveryService)
    foodItemInstance = foodItem(postcode)
    return {
        deliveryService: {
            "can_deliver": await foodItemInstance.canDeliver()
        }
    }


@app.get("/delivery/food", response_model=schemas.DeliveryServiceResponse)
async def foodDeliveryData(postcode: Union[str, None]):
    response = {}
    for foodItem in foodItems:
        foodItemInstance = foodItem(postcode)
        foodItemTask = asyncio.create_task(foodItemInstance.canDeliver())
        response[foodItemInstance.name] = foodItemTask

    for name, task in response.items():
        response[name] = {
            "can_deliver": await task
        }

    return response


@app.get("/delivery/food/{deliveryService}", response_model=schemas.DeliveryServiceResponse)
async def foodDeliveryDataPizzaHut(deliveryService: str, postcode: Union[str, None]):
    return await getResponseData(deliveryService, postcode)
