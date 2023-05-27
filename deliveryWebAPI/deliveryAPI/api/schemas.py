from pydantic import BaseModel


class CanDeliverResponse(BaseModel):
    can_deliver: bool


class DeliveryServiceResponse(BaseModel):
    __root__: dict[str, CanDeliverResponse]
