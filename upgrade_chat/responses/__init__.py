from enum import Enum

from pydantic import VERSION, BaseModel


class _Base(BaseModel):
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if VERSION >= "2.0.1":
            return super().model_validate(obj, *args, **kwargs)
        return super().parse_obj(obj, *args, **kwargs)


class Interval(Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class ProductType(Enum):
    DISCORD_ROLE = "DISCORD_ROLE"
    SHOP_PRODUCT = "SHOP_PRODUCT"


class PaymentProcessor(Enum):
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"
