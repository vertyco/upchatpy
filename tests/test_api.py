"""
To run tests locally, make a .env file in the project root with the following keys

UPGRADE_CHAT_CLIENT_ID=your_client_id
UPGRADE_CHAT_CLIENT_SECRET=your_client_secret
"""
import os
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv

from upchatpy.api import Client
from upchatpy.exceptions import AuthenticationError, ResourceNotFoundError
from upchatpy.responses.auth import AuthResponse
from upchatpy.version import __version__

load_dotenv()


client_id = os.getenv("UPGRADE_CHAT_CLIENT_ID")
client_secret = os.getenv("UPGRADE_CHAT_CLIENT_SECRET")
client = Client(client_id=client_id, client_secret=client_secret)


@pytest.mark.asyncio
async def test_version():
    assert isinstance(__version__, str)  # Duh


@pytest.mark.asyncio
async def test_get_auth():
    auth_response = await client.get_auth()
    assert hasattr(auth_response, "access_token"), "Auth response does not have access_token attribute"
    assert hasattr(auth_response, "refresh_token"), "Auth response does not have refresh_token attribute"
    assert hasattr(auth_response, "refresh_token_expires_in"), "Auth response does not have refresh_token_expires_in attribute"
    assert hasattr(auth_response, "access_token_expires_in"), "Auth response does not have access_token_expires_in attribute"
    assert hasattr(auth_response, "type"), "Auth response does not have type attribute"
    assert hasattr(auth_response, "token_type"), "Auth response does not have token_type attribute"
    assert isinstance(auth_response.access_token_expires_at, datetime), "access_token_expires_at is not a datetime object"
    assert isinstance(auth_response.refresh_token_expires_at, datetime), "refresh_token_expires_at is not a datetime object"
    assert isinstance(auth_response.access_token_expired, bool), "access_token_expired is not a boolean"
    assert isinstance(auth_response.refresh_token_expired, bool), "refresh_token_expired is not a boolean"
    new_timestamp = str(int((datetime.now() - timedelta(days=60)).timestamp() * 1000))
    auth_response.refresh_token_expires_in = new_timestamp
    assert auth_response.refresh_token_expired is True, "refresh_token_expired is not True"
    auth_response.access_token_expires_in = new_timestamp
    assert auth_response.access_token_expired is True, "access_token_expired is not True"


@pytest.mark.asyncio
async def test_model_methods():
    auth_response = await client.get_auth()
    dict_dump = auth_response.model_dump()
    assert isinstance(dict_dump, dict), "model_dump did not return a dict"
    json_dump = auth_response.model_dump_json()
    assert isinstance(json_dump, str), "model_dump_json did not return a str"
    assert isinstance(AuthResponse.model_validate(dict_dump), AuthResponse), "model_validate did not return the correct model type"
    assert isinstance(AuthResponse.model_validate_json(json_dump), AuthResponse), "model_validate_json did not return the correct model type"


@pytest.mark.asyncio
async def test_authentication():
    invalidclient = Client("invalid", "invalid")
    with pytest.raises(AuthenticationError) as exc_info:
        await invalidclient.get_orders()
        assert "Failed to authenticate" in str(exc_info.value)
    await client.get_auth()
    assert client.auth is not None, "Authentication failed, no access token obtained"


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
        assert len(orders.data) == 1, "aget Orders data length is not 1"
        if iters > 5:
            break
        iters += 1



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
        assert len(products.data) == 1, "aget Products data length is not 1"
        if iters > 5:
            break
        iters += 1


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


@pytest.mark.asyncio
async def test_user_is_subscribed():
    # You need to have a valid user ID and product UUID for this test to pass
    is_subscribed = await client.user_is_subscribed("C1eaaee5-9620-4343-b9da-bbc391c4d53f", "708960792946671707")
    assert is_subscribed is not None, "Failed to check if user is subscribed"
    assert isinstance(is_subscribed, bool), "is_subscribed is not a boolean"
    assert is_subscribed is True, "User is not subscribed to product"


@pytest.mark.asyncio
async def test_user_is_not_subscribed():
    # You need to have a valid user ID and product UUID for this test to pass
    is_subscribed = await client.user_is_subscribed("c1eaaee5-9620-4343-b9da-bbc391c4d53f", "691065892099981372")
    assert is_subscribed is not None, "Failed to check if user is subscribed"
    assert isinstance(is_subscribed, bool), "is_subscribed is not a boolean"
    assert is_subscribed is False, "User is subscribed to product"


@pytest.mark.asyncio
async def test_user_is_subscribed_notfound():
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await client.user_is_subscribed("c1eaaee5-9620-4343-b9da-test", "1111111111111111", ignore_not_found=False)
        assert "User 1111111111111111 does not exist" in str(exc_info.value)

    is_subscribed = await client.user_is_subscribed("c1eaaee5-9620-4343-b9da-bbc391c4d53f", "691065892099981372")
    assert is_subscribed is not None, "Failed to check if user is subscribed"
    assert isinstance(is_subscribed, bool), "is_subscribed is not a boolean"
    assert is_subscribed is False, "User is subscribed to product"
