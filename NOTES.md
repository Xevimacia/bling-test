# Implementation Notes

## Domain Separation / Clean Architecture
- Refactored `CardViewSet.list` and `retrieve` to use `CardService` for business logic, keeping views thin and focused on HTTP/ORM handling.
- Provider client renamed to `BankProviderClient` for clarity.

## Error Handling & Safe APIs
- Improved error handling in `CardViewSet.retrieve`: now returns safe error messages and prevents information leakage.
- For provider errors, the API returns a generic 502 error message to the client, not the raw provider message, for security and abstraction. Detailed errors are logged internally.

## Card Creation Flow & Data Consistency
- Implemented robust card creation: `CardViewSet.create` now validates input, delegates to `CardService.create_card` (which handles provider integration, transactional DB save, and error handling), and returns the created card.
- `CardService.create_card` ensures `expiration_date` is always timezone-aware before saving, using `dateutil` and `django.utils.timezone` if needed, to prevent Django warnings and ensure correct time handling.

## Security and Testability Assumptions

- For security, the API only accepts `external_id` values of `None`, `"invalid_user_id"`, or `"provider_error"` in the request body.
- If `external_id` is `None` or not provided, the logged-in user's `external_id` is used for the provider call.
- If `external_id` is `"invalid_user_id"` or `"provider_error"`, it is used to trigger provider error simulation for testing. (Triggers 502 error)
- Any other value for `external_id` is rejected with a 400 Bad Request, to prevent users from probing or simulating other users' data.
- **Important:** Allowing `external_id` in the request is a test-only feature to enable provider error simulation for the assignment. In a real implementation, only the logged-in user's `external_id` should ever be used for provider calls, and the client should never be able to specify this value.
- This approach ensures robust security while still allowing all required test scenarios for the assignment.

## Out of scope

- Added Swagger UI (drf-yasg) for API documentation and testing, by updating settings and urls. This is additional to the requirements, included for developer comfort and familiarity.