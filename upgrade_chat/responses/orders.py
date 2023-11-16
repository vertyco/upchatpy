from datetime import datetime

from . import _Base


class OrderUser(_Base):
    discord_id: str
    username: str
    email: str | None = None  # Only shows up for individual order call
    username: str | None = None  # Only shows up for individual order call


class Coupon(_Base):
    code: str
    type: str = None
    duration: str
    duration_in_months: int | None
    amount_off: float | None = None
    percent_off: float
    created: datetime


class DiscordRole(_Base):
    discord_id: str
    name: str


class Product(_Base):
    uuid: str
    name: str


class OrderItem(_Base):
    price: float
    quantity: int
    interval: str
    interval_count: int
    free_trial_length: int | None
    is_time_limited: bool
    type: str | None = None
    discord_roles: list[DiscordRole]
    product_types: list[str]
    product: Product


class Order(_Base):
    uuid: str
    purchased_at: datetime
    payment_processor: str
    payment_processor_record_id: str
    user: OrderUser
    subtotal: float
    discount: float
    total: float
    coupon_code: str | None
    coupon: Coupon | None
    type: str | None
    is_subscription: bool
    cancelled_at: datetime | None
    deleted: datetime | None
    order_items: list[OrderItem] | None


class OrdersResponse(_Base):
    """Lists Orders"""

    data: list[Order]
    total: int
    has_more: bool


class OrderResponse(_Base):
    """Retrieve Order"""

    data: Order
