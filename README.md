# Upgrade.Chat Python Wrapper

A type hinted Python wrapper for interacting with the Upgrade.Chat API.

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

### Fetching Products

Retrieve a list of products using:

```python
products_response = await client.get_products()
for product in products_response.data:
    print(product.uuid, product.name)
```

### Fetching Users

To get a list of users, you can do:

```python
users_response = await client.get_users()
for user in users_response.data:
    print(user.discord_id, user.username)
```

## Development

This package is under active development, and contributions are welcome! If you encounter any issues or have feature requests, please submit them to the project's issue tracker.

## License

This wrapper is distributed under the MIT license. See the `LICENSE` file for more information.
