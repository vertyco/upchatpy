from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import AnyUrl, Field

from . import _Base
from .enums import Interval, OrderType, ProductType, TrialAbuseCheck


class Product(_Base):
    id: int
    uuid: Optional[UUID] = Field(None, description="The UUID of the product")
    checkout_uri: Optional[AnyUrl] = Field(None, description="Direct Link to Product")
    name: Optional[str] = Field(None, description="The name of the product")
    description: Optional[str] = Field(None, description="The description of the product")
    account_id: Optional[float] = Field(None, description="The ID of the account associated with the product")
    price: Optional[float] = Field(None, description="The price of the product")
    interval: Optional[Interval] = Field(None, description="The interval of the product")
    interval_count: Optional[int] = Field(None, description="The count of intervals for the product")
    free_trial_length: Optional[float] = Field(None, description="The length of the free trial for the product")
    image_link: Optional[str] = Field(None, description="The link to the image of the product")
    color: Optional[str] = Field(None, description="The color of the product in hex format (e.g., #ffffff)")
    variable_price: Optional[bool] = Field(None, description="Indicates if the product has a variable price")
    is_time_limited: Optional[bool] = Field(None, description="Indicates if the product is time-limited")
    limited_inventory: Optional[bool] = Field(None, description="Indicates if the product has limited inventory")
    available_stock: Optional[float] = Field(None, description="The available stock of the product")
    shippable: Optional[bool] = Field(None, description="Indicates if the product is shippable")
    paymentless_trial: Optional[bool] = Field(None, description="Indicates if the product has a paymentless trial")
    required_role_id: Optional[str] = Field(None, description="The ID of the required role for the product")
    one_per_user: Optional[bool] = Field(None, description="Indicates if the product is limited to one per user")
    mailchimp_list_id: Optional[str] = Field(
        None, description="The ID of the Mailchimp list associated with the product"
    )
    unsubscribe_mailchimp_on_cancel: Optional[bool] = Field(
        None, description="Indicates if the user should be unsubscribed from the Mailchimp list on cancel"
    )
    type: Optional[OrderType] = Field(None, description="The type of the product")
    product_types: Optional[List[ProductType]] = Field(None, description="The types of the product")
    created: Optional[datetime] = Field(None, description="The creation date of the product")
    updated: Optional[datetime] = Field(None, description="The last update date of the product")
    deleted: Optional[datetime] = Field(None, description="The deletion date of the product")
    parent_id: Optional[str] = Field(None, description="The ID of the parent product")
    hidden: Optional[bool] = Field(None, description="Indicates if the product is hidden")
    slug: Optional[str] = Field(None, description="The slug of the product")
    original_price: Optional[float] = Field(None, description="The original price of the product")
    display_only: Optional[bool] = Field(None, description="Indicates if the product is for display only")
    status: Optional[str] = Field(None, description="The status of the product")
    status_code: Optional[str] = Field(None, description="The status code of the product")
    status_at: Optional[datetime] = Field(None, description="The status date of the product")
    paid_trial_length: Optional[int] = Field(None, description="The length of the paid trial for the product")
    paid_trial_price: Optional[float] = Field(None, description="The price of the paid trial for the product")
    position: Optional[int] = Field(None, description="The position of the product")
    currency_code: Optional[str] = Field(None, description="The currency code of the product")
    donatebot_product_id: Optional[str] = Field(None, description="The Donatebot product ID")
    donatebot_role_id: Optional[str] = Field(None, description="The Donatebot role ID")
    custom_trial_abuse_checks: Optional[List[TrialAbuseCheck]] = Field(
        None, description="Indicates if custom trial abuse checks are enabled"
    )
    paypal_donation: Optional[bool] = Field(None, description="Indicates if the product is a PayPal donation")


class ProductsResponse(_Base):
    """Lists products"""

    data: List[Product]
    total: int
    has_more: bool


class ProductResponse(_Base):
    """Get Product by UUID"""

    data: Product
