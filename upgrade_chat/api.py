import logging
from typing import AsyncGenerator

import aiohttp

from .responses.orders import OrderResponse, OrdersResponse
from .responses.products import ProductResponse, ProductsResponse
from .responses.users import UsersResponse

log = logging.getLogger("upgrade.chat")


class Client:
    BASE_URL = "https://api.upgrade.chat"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: str | None = None

    async def get_auth(self):
        url = f"{self.BASE_URL}/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as res:
                if res.status != 200:
                    raise Exception("Failed to authenticate with Upgrade.Chat API")
                results = await res.json()
                self.access_token = results["access_token"]

    async def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        if self.access_token is None:
            await self.get_auth()

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE_URL}{endpoint}"

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(method, url, data=data) as response:
                response.raise_for_status()
                status = response.status
                log.debug(f"{method} ({status}): {url}")
                return await response.json()

    async def aget_orders(
        self,
        limit: int = 100,
        offset: int = 0,
        user_discord_id: str | None = None,
        order_type: str | None = None,
        coupon: bool | None = None,
    ) -> AsyncGenerator[OrdersResponse, None]:
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
        user_discord_id: str | None = None,
        order_type: str | None = None,
        coupon: str | None = None,
    ) -> OrdersResponse:
        data = {
            "userDiscordId": user_discord_id,
            "type": order_type,
            "coupon": coupon,
        }
        endpoint = f"/v1/orders?limit={limit}&offset={offset}"
        for k, v in data.items():
            if v is not None:
                endpoint += f"&{k}={v}"

        response = await self._request("GET", endpoint, data=data)
        return OrdersResponse.model_validate(response)

    async def get_order(self, uuid: str) -> OrderResponse:
        response = await self._request("GET", f"/v1/orders/{uuid}")
        return OrderResponse.model_validate(response)

    async def aget_products(
        self, limit: int = 100, offset: int = 0, product_type: str | None = None
    ) -> AsyncGenerator[ProductsResponse, None]:
        offset = offset or 0
        while True:
            res = await self.get_products(limit, offset, product_type)
            yield res

            if not res.has_more:
                break
            offset += limit

    async def get_products(
        self, limit: int = 100, offset: int = 0, product_type: str | None = None
    ) -> ProductsResponse:
        data = {
            "type": product_type,
        }
        endpoint = f"/v1/products?limit={limit}&offset={offset}"
        for k, v in data.items():
            if v is not None:
                endpoint += f"&{k}={v}"

        response = await self._request("GET", endpoint, data=data)
        return ProductsResponse.model_validate(response)

    async def get_product(self, uuid: str) -> ProductResponse:
        response = await self._request("GET", f"/v1/products/{uuid}")
        return ProductResponse.model_validate(response)

    async def get_users(self, limit: int = 100, offset: int = 0) -> UsersResponse:
        data = {"limit": limit, "offset": offset}
        response = await self._request("GET", "/v1/users", data=data)
        return UsersResponse.model_validate(response)
