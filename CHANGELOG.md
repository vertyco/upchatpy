# Changelog

## [1.1.5] - 2024-12-1

### Changes

- Minor updates to error messages, includes status code in the message.
- Added additional test for os environment variables.
- Rate limit status code now checked before anything else.

## [1.1.2] - 2024-08-18

### Changes

- Added logic to handle rate limits automatically in the `Client` class. If a rate limit is hit, the client will wait for the rate limit to reset before making the request again.

## [1.1.1] - 2024-08-18

### Added

- Added missing fields to `Product` and `Order` models

## [1.1.0] - 2024-08-18

### Added

- Added `AuthResponse` class that is now returned by the `get_auth` method in the API.
- Added additional validation methods to the `_Base` class to validate
  - `model_validate_json`
  - `model_dump`
  - `model_dump_json`
- Added validation logic to ensure the `limit` parameter is between 1 and 100

### Changes

- Fixed a few bugs in the `user_is_subscribed` method for monthly and yearly subscription intervals and UUID not being lower case.
- Removed deprecated `datetime.utcnow()` call from the `user_is_subscribed` method
- `AuthResponse` can now be passed as a parameter to the Client class constructor to skip the `get_auth` method call.

### Breaking Changes

- Removed `access_tokens` attribute from the `Client` class constructor, it is now handled by the `AuthResponse` class.

## [1.0.0] - 2023-12-22

### Added

- Added `user_is_subscribed` method to the API to check if a user is currently subscribed to a product.

### Changes

- Renamed the core directory for the package, instead of using `from upgrade_chat import client` you will now use `from upchatpy import client`. Same goes for all other imports from this package.
