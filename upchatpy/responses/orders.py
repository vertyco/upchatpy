from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field

from . import _Base
from .enums import (Duration, Interval, ItemType, OrderType, PaymentProcessor,
                    ProductType)


class OrderUser(_Base):
    id: Optional[float] = None
    discord_id: Optional[str] = None

    # Only shows up for individual order call
    email: Optional[str] = None
    username: Optional[str] = None


class Coupon(_Base):
    code: Optional[str] = None
    type: Optional[ItemType] = None
    duration: Optional[Duration] = None
    duration_in_months: Optional[float] = None
    amount_off: Optional[float] = None
    percent_off: Optional[float] = None
    created: Optional[datetime] = Field(None, description="The date when the coupon was created")


class DiscordRole(_Base):
    discord_id: Optional[str] = None
    name: Optional[str] = None


class Product(_Base):
    uuid: Optional[UUID] = None
    name: Optional[str] = None


class OrderItem(_Base):
    price: Union[float, int]
    quantity: int
    interval: Optional[Interval] = None
    interval_count: Optional[int] = None
    free_trial_length: Optional[int] = None
    is_time_limited: Optional[bool] = None
    payment_procesor_record_id: Optional[str] = None
    payment_processor: PaymentProcessor
    type: Optional[ItemType] = None
    discord_roles: Optional[List[DiscordRole]] = None
    product_types: Optional[List[ProductType]] = Field(
        None,
        description="The types of the product. A product purchased through the shop will be a shop product. All other types are upgrades.",
    )
    product: Product
    product_uuid: Optional[UUID] = None


class Order(_Base):
    uuid: Optional[str] = None
    purchased_at: Optional[datetime] = None
    payment_processor: Optional[PaymentProcessor] = None
    payment_processor_record_id: Optional[str] = None
    user: Optional[OrderUser] = None
    subtotal: Optional[float] = None
    total: Optional[float] = None
    discount: Optional[float] = None
    coupon_code: Optional[str] = Field(None, description="The applied coupon code if any")
    coupon: Optional[Coupon] = Field(None, description="The applied coupon if any")
    type: Optional[OrderType] = None
    is_subscription: Optional[bool] = None
    first_invoice_due_at: Optional[datetime] = None
    upcoming_invoice_due_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = Field(None, description="The date when the subscription was cancelled")
    created: Optional[datetime] = Field(None, description="The date when the order was created")
    updated: Optional[datetime] = Field(None, description="The date when the order was last updated")
    deleted: Optional[datetime] = Field(None, description="The date when the subscription expired")
    order_items: Optional[List[OrderItem]] = None


class OrdersResponse(_Base):
    """Lists Orders"""

    data: List[Order]
    total: int
    has_more: bool


class OrderResponse(_Base):
    """Retrieve Order"""

    data: Order
