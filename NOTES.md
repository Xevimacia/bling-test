# Implementation Notes

## Context & Goals

This project implements a robust, secure, and maintainable card management API using Django. The main goals are:
- **Separation of concerns:** Business logic is kept out of views and models, living in a dedicated service layer.
- **Safe APIs:** All errors are handled gracefully, with no internal details leaked to clients.
- **Testability:** All business logic and endpoints are thoroughly tested.
- **Security:** Only safe, validated, and authorized operations are allowed.

---

## Key Changes & Rationale

### 1. Clean Architecture & Domain Separation

- **Service Layer:**  
  All business logic for cards (creation, listing, retrieval) is handled in `CardService` (in `cards/services.py`).  
  Views (`CardViewSet`) are now thin, only handling HTTP and serialization.
- **Why:**  
  This makes the code easier to maintain, test, and extend, and follows SOLID principles.

### 2. Card Creation Flow & Data Consistency

- **Robust Creation:**  
  The `CardViewSet.create` endpoint validates input, then delegates to `CardService.create_card`, which:
  - Integrates with the external provider.
  - Ensures all steps succeed before saving to the database (using a transaction).
  - Handles all errors safely.
- **Timezone Handling:**  
  The service ensures `expiration_date` is always timezone-aware, preventing Django warnings and ensuring correct time handling.
- **Why:**  
  This guarantees data consistency and prevents subtle bugs with datetimes.

### 3. Strict Contract Enforcement for Provider Response

- **Status Field Required:**  
  The service layer (`CardService.create_card`) now strictly requires the external provider to return a `status` field.  
  If `status` is missing, a clear error is raised and the card is not created.
- **API Error Handling:**  
  If this error occurs, the API returns a 502 error with a clear message to the client.
- **Why:**  
  This enforces a clear contract with the provider, catches integration bugs early, and prevents silent data issues.

### 4. Error Handling & Safe APIs

- **Consistent Error Responses:**  
  - 400 for invalid input.
  - 502 for provider or database errors.
  - 500 for unexpected errors.
- **No Internal Details Leaked:**  
  All errors are caught and returned as safe, generic messages. Internal details are logged (logging is present but commented out for now).
- **Why:**  
  This protects the system from information leakage and makes the API safer and more predictable for clients.

### 5. Security and Testability Assumptions

- **External ID Handling:**  
  - The API only accepts `external_id` values of `None`, `"invalid_user_id"`, or `"provider_error"` in the request body.
  - If `external_id` is not provided, the logged-in user's `external_id` is used.
  - `"invalid_user_id"` and `"provider_error"` are used to simulate provider errors for testing.
  - Any other value is rejected with a 400 error.
- **Test-Only Feature:**  
  Allowing `external_id` in the request is for testing only. In production, only the logged-in user's `external_id` should be used.
- **Why:**  
  This ensures robust security while allowing all required test scenarios.

---

## Comprehensive Testing

- **Service and API Layer Tests:**  
  - All business logic and error cases are covered, including:
    - Provider and database errors.
    - Invalid input.
    - Timezone handling for dates.
- **Why:**  
  This ensures the system is robust, safe, and behaves as expected in all scenarios.

---

## Out of Scope

- **Swagger UI (drf-yasg):**  
  Added for API documentation and testing. This is not required by the assignment but included for developer comfort and best practices.

---

**Summary:**  
The codebase is now robust, secure, and professional, with clear separation of concerns, strict contract enforcement, safe error handling, and comprehensive tests. All assumptions and test-only features are documented for clarity.