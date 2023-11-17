# Upgrade.Chat Python Wrapper

A type hinted async Python wrapper for interacting with the Upgrade.Chat API.

[![PyPi](https://img.shields.io/pypi/v/upchatpy)](https://pypi.org/project/upchatpy/)
[![Downloads](https://img.shields.io/pypi/dm/upchatpy)](https://pypi.org/project/upchatpy/)
![GitHub License](https://img.shields.io/github/license/vertyco/upgrade-chat)

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3913/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31011/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3116/)

[![Pydantic v1](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json)](https://docs.pydantic.dev/1.10/contributing/#badges)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)

## Introduction

This package provides a convenient and easy-to-use Python interface for the Upgrade.Chat API, allowing developers to integrate Upgrade.Chat's services into their applications. Upgrade.Chat is a platform that facilitates monetization for community services, and this wrapper aims to simplify the automation of tasks such as managing orders, products, and users.

## Installation

To install the package, run the following command:

```bash
pip install upchatpy
```

## Usage

Before you can start using the API, you need to obtain your client ID and client secret from Upgrade.Chat. Once you have them, you can begin by creating a `Client` instance:

```python
from upgrade_chat import Client

client_id = 'your_client_id'
client_secret = 'your_client_secret'

client = Client(client_id, client_secret)
```

### Authentication

The wrapper handles authentication automatically when making API calls. However, you can manually authenticate and retrieve the access token as follows:

```python
await client.get_auth()
print(client.access_token)  # Access token is now available
```

### Fetching Orders

To fetch orders, use the following method:

```python
orders_response = await client.get_orders()
for order in orders_response.data:
    print(order.uuid, order.total)
```

To fetch all orders with pagination support:

```python
async for orders_response in client.aget_orders():
    for order in orders_response.data:
        print(order.uuid, order.total)
```

To fetch a specific order by UUID:

```python
order_uuid = 'your_order_uuid'
order_response = await client.get_order(order_uuid)
print(order_response.data.total)
```

### Fetching Products

Fetch a list of products using:

```python
products_response = await client.get_products()
for product in products_response.data:
    print(product.uuid, product.name)
```

To fetch all products with pagination support:

```python
async for products_response in client.aget_products():
    for product in products_response.data:
        print(product.uuid, product.name)
```

To fetch a product order by UUID:

```python
product_uuid = 'your_product_uuid'
product_response = await client.get_product(product_uuid)
print(product_response.data.name)
```

### Fetching Users

To get a list of users, you can do:

```python
users_response = await client.get_users()
for user in users_response.data:
    print(user.discord_id, user.username)
```

### Fetching Webhooks

Fetch a list of webhooks using:

```python
webhooks_response = await client.get_webhooks()
for webhook in webhooks_response.data:
    print(webhook.id, webhook.uri)
```

To fetch all webhooks with pagination support:

```python
async for webhooks_response in client.aget_webhooks():
    for webhook in webhooks_response.data:
        print(webhook.id, webhook.url)
```

To fetch a specific webhook by ID:

```python
webhook_id = 'your_webhook_id'
webhook_response = await client.get_webhook(webhook_id)
print(webhook_response.data.id, webhook_response.data.url)
```

### Fetching Webhook Events

Fetch a list of webhooks events using:

```python
webhook_events_response = await client.get_webhook_events()
for webhook_event in webhook_events_response.data:
    print(webhook_event.id, webhook_event.webhook_id)
```

To fetch a list of webhook events with pagination support:

```python
async for webhook_events_response in client.aget_webhook_events():
    for webhook_event in webhook_events_response.data:
        print(webhook_event.id, webhook_event.webhook_id)
```

To fetch a specific webhook event by ID:

```python
event_id = 'your_event_id'
webhook_event_response = await client.get_webhook_event(event_id)
print(webhook_event_response.data.id)
```

### Validating Webhook Events

To validate a webhook event by ID:

```python
event_id = 'your_event_id'
webhook_valid_response = await client.validate_webhook_event(event_id)
print(webhook_valid_response.data.is_valid)
```

## Exception Handling

The Upgrade.Chat Python Wrapper provides custom exceptions to help you handle potential errors that may occur during API interaction.

### Custom Exceptions

- `AuthenticationError`: Raised when there is a problem with client authentication, such as incorrect client ID or client secret.
- `HTTPError`: Raised for general HTTP-related errors when making API requests.
- `ResourceNotFoundError`: Raised when a requested resource is not found on the Upgrade.Chat API.

### Example Usage

```python
from upgrade_chat import Client
from upgrade_chat.exceptions import AuthenticationError, HTTPError, ResourceNotFoundError

client_id = 'your_client_id'
client_secret = 'your_client_secret'
client = Client(client_id, client_secret)

async def main():
    try:
        orders_response = await client.get_orders()
        for order in orders_response.data:
            print(order.uuid, order.total)
    except AuthenticationError as e:
        print(f"Authentication failed with status code {e.status_code}: {e.message}")
    except ResourceNotFoundError as e:
        print(f"Resource not found with status code {e.status_code}: {e.message}")
    except HTTPError as e:
        print(f"HTTP error with status code {e.status_code}: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
```

## Development

This package is under active development, and contributions are welcome! If you encounter any issues or have feature requests, please submit them to the project's issue tracker.

## License

This wrapper is distributed under the MIT license. See the `LICENSE` file for more information.
