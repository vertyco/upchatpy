from __future__ import annotations

from typing import List, Optional

from pydantic import AnyUrl

from . import _Base
from .enums import EventType
from .orders import Order


class Webhook(_Base):
    id: Optional[str] = None
    uri: Optional[AnyUrl] = None


class WebhookEvent(_Base):
    id: Optional[str] = None
    webhook_id: Optional[str] = None
    type: Optional[EventType] = None
    body: Optional[Order] = None
    attempts: Optional[float] = None


class WebhookEventsResponse(_Base):
    """Lists Webhook Events"""

    data: List[WebhookEvent]
    total: int
    has_more: bool


class WebhookEventResponse(_Base):
    """Get Webhook Event by Id"""

    data: WebhookEvent


class WebhookValidResponse(_Base):
    """Validate a webhook event"""

    valid: bool


class WebhooksResponse(_Base):
    """List Webhooks"""

    data: List[Webhook]
    total: int
    has_more: bool


class WebhookResponse(_Base):
    """Get Webhook by Id"""

    data: Webhook
