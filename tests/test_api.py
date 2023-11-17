"""
To run tests locally, make a .env file in the project root with the following keys

UPGRADE_CHAT_CLIENT_ID=your_client_id
UPGRADE_CHAT_CLIENT_SECRET=your_client_secret
"""
import os

import pytest
from dotenv import load_dotenv

from upgrade_chat.api import Client
from upgrade_chat.exceptions import AuthenticationError, ResourceNotFoundError
from upgrade_chat.version import __version__

load_dotenv()

client_id = os.getenv("UPGRADE_CHAT_CLIENT_ID")
client_secret = os.getenv("UPGRADE_CHAT_CLIENT_SECRET")
client = Client(client_id=client_id, client_secret=client_secret)


@pytest.mark.asyncio
async def test_version():
    assert isinstance(__version__, str)  # Duh


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
    if orders_response.data:
        valid_uuid = orders_response.data[0].uuid
        order_response = await client.get_order(valid_uuid)
        assert order_response is not None, "Failed to fetch order"
        assert hasattr(order_response, "data"), "Order response does not have data attribute"
    else:
        pytest.skip("No orders available to test")


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
    if products_response.data:
        valid_uuid = products_response.data[0].uuid
        product_response = await client.get_product(valid_uuid)
        assert product_response is not None, "Failed to fetch product"
        assert hasattr(product_response, "data"), "Product response does not have data attribute"
    else:
        pytest.skip("No products available to test")


@pytest.mark.asyncio
async def test_get_users():
    users_response = await client.get_users()
    assert users_response is not None, "Failed to fetch users"
    assert hasattr(users_response, "data"), "Users response does not have data attribute"
    assert isinstance(users_response.data, list), "Users data is not a list"


@pytest.mark.asyncio
async def test_get_webhooks():
    webhooks_response = await client.get_webhooks()
    assert webhooks_response is not None, "Failed to fetch webhooks"
    assert hasattr(webhooks_response, "data"), "Webhooks response does not have data attribute"
    assert isinstance(webhooks_response.data, list), "Webhooks data is not a list"

    iters = 1
    async for webhooks in client.aget_webhooks(limit=1):
        assert webhooks is not None, "aget Failed to fetch webhooks"
        assert hasattr(webhooks, "data"), "aget webhooks response does not have data attribute"
        assert isinstance(webhooks.data, list), "aget webhooks data is not a list"
        iters += 1
        if iters > 2:
            break


@pytest.mark.asyncio
async def test_get_webhook():
    # You need to have a valid webhook ID for this test to pass
    webhooks_response = await client.get_webhooks()
    if webhooks_response.data:
        valid_webhook_id = webhooks_response.data[0].id
        webhook_response = await client.get_webhook(valid_webhook_id)
        assert webhook_response is not None, "Failed to fetch webhook"
        assert hasattr(webhook_response, "data"), "Webhook response does not have data attribute"
    else:
        pytest.skip("No webhooks available to test")


@pytest.mark.asyncio
async def test_get_webhook_events():
    webhook_events_response = await client.get_webhook_events()
    assert webhook_events_response is not None, "Failed to fetch webhook events"
    assert hasattr(webhook_events_response, "data"), "Webhook events response does not have data attribute"
    assert isinstance(webhook_events_response.data, list), "Webhook events data is not a list"

    iters = 1
    async for webhook_events in client.aget_webhook_events(limit=1):
        assert webhook_events is not None, "aget Failed to fetch webhook events"
        assert hasattr(webhook_events, "data"), "aget webhook events response does not have data attribute"
        assert isinstance(webhook_events.data, list), "aget webhook events data is not a list"
        iters += 1
        if iters > 2:
            break


@pytest.mark.asyncio
async def test_get_webhook_event():
    # You need to have a valid webhook event ID for this test to pass
    webhook_events_response = await client.get_webhook_events()
    if webhook_events_response.data:
        valid_event_id = webhook_events_response.data[0].id
        webhook_event_response = await client.get_webhook_event(valid_event_id)
        assert webhook_event_response is not None, "Failed to fetch webhook event"
        assert hasattr(webhook_event_response, "data"), "Webhook event response does not have data attribute"
    else:
        pytest.skip("No webhook events available to test")


@pytest.mark.asyncio
async def test_validate_webhook_event():
    # You need to have a valid webhook event ID for this test to pass
    webhook_events_response = await client.get_webhook_events()
    if webhook_events_response.data:
        valid_event_id = webhook_events_response.data[0].id
        webhook_valid_response = await client.validate_webhook_event(valid_event_id)
        assert webhook_valid_response is not None, "Failed to validate webhook event"
        assert hasattr(webhook_valid_response, "valid"), "Webhook valid response does not have valid attribute"
        assert isinstance(webhook_valid_response.valid, bool), "Webhook valid attribute is not a boolean"
    else:
        pytest.skip("No webhook events available to validate")
