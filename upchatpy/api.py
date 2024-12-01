"""
MIT License

Copyright (c) 2023 Vertyco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import AsyncGenerator, List, Literal, Optional
from urllib.parse import urlencode

import aiohttp

from .exceptions import AuthenticationError, HTTPError, ResourceNotFoundError
from .responses.auth import AuthResponse
from .responses.orders import Order, OrderItem, OrderResponse, OrdersResponse
from .responses.products import ProductResponse, ProductsResponse
from .responses.users import UsersResponse
from .responses.webhooks import (WebhookEventResponse, WebhookEventsResponse,
                                 WebhookResponse, WebhooksResponse,
                                 WebhookValidResponse)

log = logging.getLogger("upgrade.chat")


class Client:
    """Upgrade.Chat API has a global rate limit of 10 requests per 10 seconds. (so 1/s with some burst tolerance)"""

    BASE_URL = "https://api.upgrade.chat"
    RATE_LIMIT = 10
    RATE_PERIOD = 10  # seconds

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth: Optional[AuthResponse] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initializes the Client with the provided client ID and client secret.

        Args:
            client_id (str): The client ID obtained from Upgrade.Chat.
            client_secret (str): The client secret obtained from Upgrade.Chat.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth = auth
        self.timeout = timeout

        self._calls: List[float] = []

    async def _handle_rate_limit(self):
        """
        Handles the rate limit by waiting until the rate limit period has passed.
        """
        current_time = datetime.now().timestamp()
        self._calls = [timestamp for timestamp in self._calls if current_time - timestamp < self.RATE_PERIOD]

        if len(self._calls) >= self.RATE_LIMIT:
            wait_time = self.RATE_PERIOD - (current_time - self._calls[0])
            log.info("Rate limit reached, waiting for %s seconds", wait_time)
            await asyncio.sleep(wait_time)

    async def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Internal method to send HTTP requests to the Upgrade.Chat API.

        Args:
            method (str): The HTTP method to use ('GET', 'POST', etc.).
            endpoint (str): The API endpoint to request.
            data (dict, optional): Optional dictionary of data to send with the request. Defaults to None.

        Raises:
            ResourceNotFoundError: Raised if user or product doesn't exist ect.
            HTTPError: Raised during a ClientResponse error.

        Returns:
            dict: The JSON response as a dictionary.
        """

        headers = None
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        if endpoint != "/oauth/token":
            if self.auth is None:
                log.debug("No auth token, fetching")
                await self.get_auth()
            elif self.auth.access_token_expired:
                log.debug("Access token expired, refreshing")
                await self.get_auth()
            headers = {"Authorization": f"Bearer {self.auth.access_token}"}
        elif self.auth is not None:  # get_auth called even though we have an auth token
            # Trying to re-authorize? check if token is expired
            if not self.auth.access_token_expired:
                # get_auth was needlessly called, dont waste a request and just return the model dump
                return self.auth.model_dump(mode="json")

        await self._handle_rate_limit()

        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                while True:
                    async with session.request(method, f"{self.BASE_URL}{endpoint}", data=data) as response:
                        log.debug("%s, (%s): %s", method, response.status, response.url)
                        if response.status == 429:
                            wait = int(response.headers.get("Retry-After", 60))
                            log.warning("We are being rate limited, trying again in %s seconds", wait)
                            await asyncio.sleep(wait)
                            continue
                        elif response.status != 200 and endpoint == "/oauth/token":
                            msg = f"[{response.status}] Failed to authenticate with Upgrade.Chat API"
                            if response.status == 400:
                                msg += " (Make sure client ID and secret are correct)"
                            raise AuthenticationError(response.status, msg)
                        elif response.status == 404:
                            error_details = await response.json()
                            message = error_details.get("message", "404 Resource not found")
                            raise ResourceNotFoundError(response.status, f"[{response.status}] {message}")
                        elif response.status == 401:
                            log.warning("Authentication failed, re-authenticating")
                            await self.get_auth()
                            continue
                        response.raise_for_status()
                        self._calls.append(datetime.now().timestamp())
                        return await response.json()
        except aiohttp.ClientResponseError as e:
            raise HTTPError(e.status, e.message)

    async def get_auth(self) -> AuthResponse:
        """
        Authenticates the client and retrieves the access token from Upgrade.Chat.

        Raises:
            AuthenticationError: if authentication fails.

        Returns:
            AuthResponse: The authentication response.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = await self._request("POST", "/oauth/token", data)
        self.auth = AuthResponse.model_validate(response)
        return self.auth

    async def aget_orders(
        self,
        limit: int = 100,
        offset: int = 0,
        user_discord_id: Optional[str] = None,
        order_type: Optional[Literal["SHOP", "UPGRADE"]] = None,
        coupon: Optional[bool] = None,
    ) -> AsyncGenerator[OrdersResponse, None]:
        """
        Fetches orders with pagination support.

        Args:
            limit (int, optional): The maximum number of orders to retrieve per page. Defaults to 100 (max is 100).
            offset (int, optional): The offset to start retrieving orders from. Defaults to 0.
            user_discord_id (Optional[str], optional): Filter orders for a specific Discord user ID. Defaults to None.
            order_type (Optional[str], optional): Filter orders by type. Defaults to None.
            coupon (Optional[str], optional): Filter orders by coupon. Defaults to None.

        Returns:
            AsyncGenerator[OrdersResponse, None]: An async generator yielding OrdersResponse objects.

        Yields:
            Iterator[AsyncGenerator[OrdersResponse, None]]: OrdersResponse object
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        offset = offset or 0
        while True:
            res = await self.get_orders(limit, offset, user_discord_id, order_type, coupon)
            yield res

            if not res.has_more:
                break
            offset += limit

    async def get_orders(
        self,
        limit: int = 100,
        offset: int = 0,
        user_discord_id: Optional[str] = None,
        order_type: Optional[Literal["SHOP", "UPGRADE"]] = None,
        coupon: Optional[str] = None,
    ) -> OrdersResponse:
        """
        Fetches a list of orders from the Upgrade.Chat API.

        Args:
            limit (int, optional): The maximum number of orders to retrieve per page. Defaults to 100 (max is 100).
            offset (int, optional): The offset to start retrieving orders from. Defaults to 0.
            user_discord_id (Optional[str], optional): Filter orders for a specific Discord user ID. Defaults to None.
            order_type (Optional[str], optional): Filter orders by type. Defaults to None.
            coupon (Optional[str], optional): Filter orders by coupon. Defaults to None.

        Returns:
            OrdersResponse: An OrdersResponse object containing the fetched orders.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        query_params = {
            "limit": limit,
            "offset": offset,
            "userDiscordId": user_discord_id,
            "type": order_type,
            "coupon": coupon,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        query_string = urlencode(query_params)
        endpoint = f"/v1/orders?{query_string}"
        response = await self._request("GET", endpoint)
        return OrdersResponse.model_validate(response)

    async def get_order(self, uuid: str) -> OrderResponse:
        """
        Fetches a single order by UUID from the Upgrade.Chat API.

        Args:
            uuid (str): The UUID of the order to retrieve.

        Returns:
            OrderResponse: An OrderResponse object containing the order details.
        """
        response = await self._request("GET", f"/v1/orders/{uuid}")
        return OrderResponse.model_validate(response)

    async def aget_products(
        self, limit: int = 100, offset: int = 0, product_type: Optional[str] = None
    ) -> AsyncGenerator[ProductsResponse, None]:
        """
        Fetches products with pagination support.

        Args:
            limit (int, optional): The number of products to fetch per request. Defaults to 100 (max is 100).
            offset (int, optional): The offset from where to start fetching products. Defaults to 0.
            product_type (Optional[str], optional): Optional product type to filter products. Defaults to None.

        Returns:
            AsyncGenerator[ProductsResponse, None]: An async generator yielding ProductsResponse objects.

        Yields:
            Iterator[AsyncGenerator[ProductsResponse, None]]: ProductsResponse object.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        offset = offset or 0
        while True:
            res = await self.get_products(limit, offset, product_type)
            yield res

            if not res.has_more:
                break
            offset += limit

    async def get_products(
        self, limit: int = 100, offset: int = 0, product_type: Optional[str] = None
    ) -> ProductsResponse:
        """
        Asynchronously fetches products with pagination support.

        Args:
            limit (int, optional): The number of products to fetch per request. Defaults to 100 (max is 100).
            offset (int, optional): The offset from where to start fetching products. Defaults to 0.
            product_type (Optional[str], optional): Optional product type to filter products. Defaults to None.

        Returns:
            ProductsResponse: A ProductsResponse object containing the fetched products.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        query_params = {
            "limit": limit,
            "offset": offset,
            "type": product_type,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        query_string = urlencode(query_params)
        endpoint = f"/v1/products?{query_string}"

        response = await self._request("GET", endpoint)
        return ProductsResponse.model_validate(response)

    async def get_product(self, uuid: str) -> ProductResponse:
        """
        Fetches a single product by UUID from the Upgrade.Chat API.

        Args:
            uuid (str): The UUID of the product to retrieve.

        Returns:
            ProductResponse: A ProductResponse object containing the product details.
        """
        response = await self._request("GET", f"/v1/products/{uuid}")
        return ProductResponse.model_validate(response)

    async def get_users(self, limit: int = 100, offset: int = 0) -> UsersResponse:
        """Fetches a list of users from the Upgrade.Chat API.

        Args:
            limit (int, optional): The maximum number of users to retrieve. Defaults to 100 (max is 100).
            offset (int, optional): The offset to start retrieving users from. Defaults to 0.

        Returns:
            UsersResponse: A UsersResponse object containing the fetched users.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        query_params = {"limit": limit, "offset": offset}
        query_string = urlencode(query_params)
        endpoint = f"/v1/users?{query_string}"

        response = await self._request("GET", endpoint)
        return UsersResponse.model_validate(response)

    async def aget_webhooks(self, limit: int = 100, offset: int = 0) -> AsyncGenerator[WebhooksResponse, None]:
        """
        Fetches a list of webhooks with pagination support

        Args:
            limit (int): The maximum number of webhooks to retrieve, defaults to 100 (max is 100).
            offset (int): The offset to start retrieving webhooks from, this will increment by the limit each iteration.

        Returns:
            AsyncGenerator[WebhooksResponse, None]: An async generator yielding WebhooksResponse objects.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        offset = offset or 0
        while True:
            res = await self.get_webhooks(limit, offset)
            yield res

            if not res.has_more:
                break
            offset += limit

    async def get_webhooks(self, limit: int = 100, offset: int = 0) -> WebhooksResponse:
        """
        Fetches a list of webhooks.

        Args:
            limit (int): The maximum number of webhooks to retrieve, defaults to 100 (max is 100).
            offset (int): The offset to start retrieving webhooks from.

        Returns:
            WebhooksResponse: A WebhooksResponse object containing the fetched webhooks.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        query_params = {"limit": limit, "offset": offset}
        query_string = urlencode(query_params)
        endpoint = f"/v1/webhooks?{query_string}"

        response = await self._request("GET", endpoint)
        return WebhooksResponse.model_validate(response)

    async def get_webhook(self, webhook_id: str) -> WebhookResponse:
        """
        Fetches a single webhook by ID.

        Args:
            webhook_id (str): The ID of the webhook to retrieve.

        Returns:
            WebhookResponse: A WebhookResponse object containing the webhook details.
        """
        response = await self._request("GET", f"/v1/webhooks/{webhook_id}")
        return WebhookResponse.model_validate(response)

    async def aget_webhook_events(
        self, limit: int = 100, offset: int = 0
    ) -> AsyncGenerator[WebhookEventsResponse, None]:
        """
        Fetches a list of webhooks events with pagination support

        Args:
            limit (int): The maximum number of webhooks to retrieve, defaults to 100 (max is 100).
            offset (int): The offset to start retrieving webhooks from, this will increment by the limit each iteration.

        Returns:
            AsyncGenerator[WebhookEventsResponse, None]: An async generator yielding WebhookEventsResponse objects.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        offset = offset or 0
        while True:
            res = await self.get_webhook_events(limit, offset)
            yield res

            if not res.has_more:
                break
            offset += limit

    async def get_webhook_events(self, limit: int = 100, offset: int = 0) -> WebhookEventsResponse:
        """
        Fetches a list of webhook events.

        Args:
            limit (int): The maximum number of webhook events to retrieve, defaults to 100 (max is 100).
            offset (int): The offset to start retrieving webhook events from.

        Returns:
            WebhookEventsResponse: A WebhookEventsResponse object containing the fetched webhook events.
        """
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100")
        query_params = {"limit": limit, "offset": offset}
        query_string = urlencode(query_params)
        endpoint = f"/v1/webhook-events?{query_string}"

        response = await self._request("GET", endpoint)
        return WebhookEventsResponse.model_validate(response)

    async def get_webhook_event(self, event_id: str) -> WebhookEventResponse:
        """
        Fetches a single webhook event by ID.

        Args:
            event_id (str): The ID of the webhook event to retrieve.

        Returns:
            WebhookEventResponse: A WebhookEventResponse object containing the webhook event details.
        """
        response = await self._request("GET", f"/v1/webhook-events/{event_id}")
        return WebhookEventResponse.model_validate(response)

    async def validate_webhook_event(self, event_id: str) -> WebhookValidResponse:
        """
        Validates a webhook event by ID.

        Args:
            event_id (str): The ID of the webhook event to validate.

        Returns:
            WebhookValidResponse: A WebhookValidResponse object indicating if the event is valid.
        """
        response = await self._request("GET", f"/v1/webhook-events/{event_id}/validate")
        return WebhookValidResponse.model_validate(response)

    async def user_is_subscribed(
        self,
        product_uuid: str,
        user_discord_id: str,
        include_cancelled: bool = True,
        ignore_not_found: bool = True,
    ) -> bool:
        """
        Checks if a user is currently subscribed to a product.

        Args:
            product_uuid (str): The UUID of the product to check.
            user_discord_id (str): The Discord ID of the user to check.
            include_cancelled (bool, optional): If true, will consider a cancelled subscription with time left as still subscribed. Defaults to True.
            ignore_not_found (bool, optional): If false, will raise an exception if the user does not exist. Defaults to True.

        Returns:
            bool: True if the user is subscribed to the product, False otherwise.
        """
        user_orders: list[Order] = []
        product_uuid = product_uuid.lower()

        try:
            async for orders in self.aget_orders(user_discord_id=user_discord_id, order_type="UPGRADE"):
                for order in orders.data:
                    if not order.purchased_at:
                        continue
                    if not order.order_items:
                        continue
                    if not order.is_subscription:
                        continue
                    if order.deleted is not None:
                        # Check if the deleted date has passed
                        if order.deleted < datetime.now(UTC):
                            continue
                    if str(order.order_items[0].product.uuid) != product_uuid:
                        continue
                    user_orders.append(order)
        except ResourceNotFoundError:
            if not ignore_not_found:
                raise
            log.debug("User %s does not exist in Upgrade.Chat", user_discord_id)
            return False

        if not user_orders:
            log.debug("User %s has no orders for product %s", user_discord_id, product_uuid)
            return False

        # Sort orders by purchased_at date with the most recent first
        user_orders.sort(key=lambda x: x.purchased_at, reverse=True)

        most_recent_order: Order = user_orders[0]
        if most_recent_order.deleted is not None:
            # Subscription is still active
            log.debug(
                "User %s's subscription for %s is active but will be deleted on %s",
                user_discord_id,
                product_uuid,
                most_recent_order.deleted,
            )
            return True

        if not most_recent_order.cancelled_at:
            log.debug("User %s is subscribed to product %s", user_discord_id, product_uuid)
            return True

        # Order has a cancel date
        if not include_cancelled:
            log.debug(
                "User %s's subscription to product %s is cancelled and will be considered inactive",
                user_discord_id,
                product_uuid,
            )
            return False

        if not most_recent_order.order_items or not most_recent_order.purchased_at:
            # This wont happen but we'll raise an error just in case
            raise ValueError(f"Order {most_recent_order.uuid} has no order items or purchased_at date")

        # Check if the cancelled subscription has time left
        order_item: OrderItem = most_recent_order.order_items[0]
        purchased_at = most_recent_order.purchased_at
        interval = order_item.interval.value
        interval_count = order_item.interval_count or 1
        if interval == "day":
            expires_on = purchased_at + timedelta(days=interval_count)
        elif interval == "week":
            expires_on = purchased_at + timedelta(weeks=interval_count)
        elif interval == "month":
            expires_on = purchased_at + timedelta(days=interval_count * 30)
        elif interval == "year":
            expires_on = purchased_at + timedelta(days=interval_count * 365)
        else:
            raise ValueError(f"Unknown interval type for order {most_recent_order.uuid}, interval: {interval}")

        if expires_on > datetime.now(UTC):
            log.debug("User %s's sub to product %s is active but ends on %s", user_discord_id, product_uuid, expires_on)
            return True

        log.debug("User %s is not subscribed to product %s", user_discord_id)
        return False
