import os

import pytest
from dotenv import load_dotenv

from upgrade_chat.api import Client
from upgrade_chat.exceptions import AuthenticationError, ResourceNotFoundError

load_dotenv()

client_id = os.getenv("UPGRADE_CHAT_CLIENT_ID")
client_secret = os.getenv("UPGRADE_CHAT_CLIENT_SECRET")
client = Client(client_id=client_id, client_secret=client_secret)


@pytest.mark.asyncio
async def test_authentication():
    invalidclient = Client("invalid", "invalid")
    with pytest.raises(AuthenticationError) as exc_info:
        await invalidclient.get_orders()
        assert "Failed to authenticate" in str(exc_info.value)
    await client.get_auth()
    assert client.access_token is not None, "Authentication failed, no access token obtained"


@pytest.mark.asyncio
async def test_get_orders():
    orders_response = await client.get_orders()
    assert orders_response is not None, "Failed to fetch orders"
    assert hasattr(orders_response, "data"), "Orders response does not have data attribute"
    assert isinstance(orders_response.data, list), "Orders data is not a list"

    iters = 1
    async for orders in client.aget_orders(limit=1):
        assert orders is not None, "aget Failed to fetch orders"
        assert hasattr(orders, "data"), "aget Orders response does not have data attribute"
        assert isinstance(orders.data, list), "aget Orders data is not a list"
        iters += 1
        if iters > 2:
            break


@pytest.mark.asyncio
async def test_get_orders_invalid_discord_id():
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await client.get_orders(user_discord_id="35005350581528166")
        assert "User 35005350581528166 does not exist" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_order():
    # You need to have a valid UUID for this test to pass
    orders_response = await client.get_orders()
    valid_uuid = orders_response.data[0].uuid
    order_response = await client.get_order(valid_uuid)
    assert order_response is not None, "Failed to fetch order"
    assert hasattr(order_response, "data"), "Order response does not have data attribute"


@pytest.mark.asyncio
async def test_get_products():
    products_response = await client.get_products()
    assert products_response is not None, "Failed to fetch products"
    assert hasattr(products_response, "data"), "Products response does not have data attribute"
    assert isinstance(products_response.data, list), "Products data is not a list"

    iters = 1
    async for products in client.aget_products(limit=1):
        assert products is not None, "aget Failed to fetch products"
        assert hasattr(products, "data"), "aget Products response does not have data attribute"
        assert isinstance(products.data, list), "aget Products data is not a list"
        iters += 1
        if iters > 2:
            break


@pytest.mark.asyncio
async def test_get_product():
    # You need to have a valid UUID for this test to pass
    products_response = await client.get_products()
    valid_uuid = products_response.data[0].uuid
    product_response = await client.get_product(valid_uuid)
    assert product_response is not None, "Failed to fetch product"
    assert hasattr(product_response, "data"), "Product response does not have data attribute"


@pytest.mark.asyncio
async def test_get_users():
    users_response = await client.get_users()
    assert users_response is not None, "Failed to fetch users"
    assert hasattr(users_response, "data"), "Users response does not have data attribute"
    assert isinstance(users_response.data, list), "Users data is not a list"
