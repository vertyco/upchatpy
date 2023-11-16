from datetime import datetime
from typing import List

from . import _Base


class Product(_Base):
    uuid: str
    checkout_uri: str
    name: str
    account_id: int
    price: float
    interval: str | None
    interval_count: int | None
    free_trial_length: int | None
    description: str
    image_link: str | None
    variable_price: bool
    is_time_limited: bool
    limited_inventory: bool
    available_stock: int | None
    shippable: bool
    paymentless_trial: bool
    product_types: list[str]
    created: datetime
    updated: datetime
    deleted: datetime | None


class ProductsResponse(_Base):
    """Lists products"""

    data: List[Product]
    total: int
    has_more: bool


class ProductResponse(_Base):
    """Get Product by UUID"""

    data: Product
