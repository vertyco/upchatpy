from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import AnyUrl, Field

from . import Interval, ProductType, _Base


class Product(_Base):
    uuid: Optional[UUID] = None
    checkout_uri: Optional[AnyUrl] = Field(None, description="Direct Link to Product")
    name: Optional[str] = None
    account_id: Optional[float] = None
    price: Optional[float] = None
    interval: Optional[Interval] = None
    interval_count: Optional[int] = None
    free_trial_length: Optional[float] = None
    description: Optional[str] = None
    image_link: Optional[str] = None
    variable_price: Optional[bool] = None
    is_time_limited: Optional[bool] = None
    limited_inventory: Optional[bool] = None
    available_stock: Optional[float] = None
    shippable: Optional[bool] = None
    paymentless_trial: Optional[bool] = None
    product_types: Optional[List[ProductType]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    deleted: Optional[datetime] = None


class ProductsResponse(_Base):
    """Lists products"""

    data: List[Product]
    total: int
    has_more: bool


class ProductResponse(_Base):
    """Get Product by UUID"""

    data: Product
