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

import logging
from typing import AsyncGenerator, Optional
from urllib.parse import urlencode

import aiohttp

from .exceptions import AuthenticationError, HTTPError, ResourceNotFoundError
from .responses.orders import OrderResponse, OrdersResponse
from .responses.products import ProductResponse, ProductsResponse
from .responses.users import UsersResponse

log = logging.getLogger("upgrade.chat")


class Client:
    BASE_URL = "https://api.upgrade.chat"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initializes the Client with the provided client ID and client secret.

        Args:
            client_id (str): The client ID obtained from Upgrade.Chat.
            client_secret (str): The client secret obtained from Upgrade.Chat.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None

    async def get_auth(self) -> None:
        """
        Authenticates the client and retrieves the access token from Upgrade.Chat.

        Raises:
            AuthenticationError: if authentication fails.
        """
        url = f"{self.BASE_URL}/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as res:
                if res.status != 200:
                    raise AuthenticationError(res.status, "Failed to authenticate with Upgrade.Chat API")
                results = await res.json()
                self.access_token = results["access_token"]

    async def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
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
        if self.access_token is None:
            await self.get_auth()

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method, url, data=data) as response:
                    log.debug(f"{method} ({response.status}): {url}")

                    if response.status == 404:
                        error_details = await response.json()
                        message = error_details.get("message", "Resource not found")
                        raise ResourceNotFoundError(response.status, message)

                    response.raise_for_status()

                    return await response.json()

        except aiohttp.ClientResponseError as e:
            raise HTTPError(e.status, e.message)

    async def aget_orders(
        self,
        limit: int = 100,
        offset: int = 0,
        user_discord_id: Optional[str] = None,
        order_type: Optional[str] = None,
        coupon: Optional[bool] = None,
    ) -> AsyncGenerator[OrdersResponse, None]:
        """
        Asynchronously fetches orders with pagination support.

        Args:
            limit (int, optional): The maximum number of orders to retrieve per page. Defaults to 100.
            offset (int, optional): The offset to start retrieving orders from. Defaults to 0.
            user_discord_id (Optional[str], optional): Filter orders for a specific Discord user ID. Defaults to None.
            order_type (Optional[str], optional): Filter orders by type. Defaults to None.
            coupon (Optional[str], optional): Filter orders by coupon. Defaults to None.

        Returns:
            AsyncGenerator[OrdersResponse, None]: An async generator yielding OrdersResponse objects.

        Yields:
            Iterator[AsyncGenerator[OrdersResponse, None]]: OrdersResponse object
        """
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
        order_type: Optional[str] = None,
        coupon: Optional[str] = None,
    ) -> OrdersResponse:
        """
        Fetches a list of orders from the Upgrade.Chat API.

        Args:
            limit (int, optional): The maximum number of orders to retrieve per page. Defaults to 100.
            offset (int, optional): The offset to start retrieving orders from. Defaults to 0.
            user_discord_id (Optional[str], optional): Filter orders for a specific Discord user ID. Defaults to None.
            order_type (Optional[str], optional): Filter orders by type. Defaults to None.
            coupon (Optional[str], optional): Filter orders by coupon. Defaults to None.

        Returns:
            OrdersResponse: An OrdersResponse object containing the fetched orders.
        """
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
        Asynchronously fetches products with pagination support.

        Args:
            limit (int, optional): The number of products to fetch per request. Defaults to 100.
            offset (int, optional): The offset from where to start fetching products. Defaults to 0.
            product_type (Optional[str], optional): Optional product type to filter products. Defaults to None.

        Returns:
            AsyncGenerator[ProductsResponse, None]: An async generator yielding ProductsResponse objects.

        Yields:
            Iterator[AsyncGenerator[ProductsResponse, None]]: ProductsResponse object.
        """
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
            limit (int, optional): The number of products to fetch per request. Defaults to 100.
            offset (int, optional): The offset from where to start fetching products. Defaults to 0.
            product_type (Optional[str], optional): Optional product type to filter products. Defaults to None.

        Returns:
            ProductsResponse: A ProductsResponse object containing the fetched products.
        """
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
            limit (int, optional): The maximum number of users to retrieve. Defaults to 100.
            offset (int, optional): The offset to start retrieving users from. Defaults to 0.

        Returns:
            UsersResponse: A UsersResponse object containing the fetched users.
        """
        query_params = {"limit": limit, "offset": offset}
        query_string = urlencode(query_params)
        endpoint = f"/v1/users?{query_string}"

        response = await self._request("GET", endpoint)
        return UsersResponse.model_validate(response)
