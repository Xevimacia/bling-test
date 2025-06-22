from rest_framework.exceptions import APIException

class ServiceException(APIException):
    """Base class for service-level exceptions."""
    pass

class UserNotRegisteredError(ServiceException):
    """Raised when the user is not registered with the provider."""
    status_code = 400
    default_detail = {
        "error": "user_not_registered",
        "message": "User is not registered for card issuance.",
    }
    default_code = 'user_not_registered'


class ProviderFailureError(ServiceException):
    """Raised when the provider experiences an internal failure."""
    status_code = 502  # Bad Gateway
    default_detail = {
        "error": "provider_unavailable",
        "message": "The card provider is temporarily unavailable. Please try again later.",
    }
    default_code = 'provider_unavailable'


class InvalidCardDataError(ServiceException):
    """Raised for invalid card data, like past expiration dates."""
    status_code = 400
    default_detail = {
        "error": "invalid_card_data",
        "message": "The data received from the provider was invalid.",
    }
    default_code = 'invalid_card_data'


class InvalidInputError(ServiceException):
    """Raised for invalid input provided by the client."""
    status_code = 400
    default_detail = {
        "error": "invalid_input",
        "message": "The provided input is invalid.",
    }
    default_code = 'invalid_input'


class CardNotFoundError(ServiceException):
    """Raised when a specific card is not found for the user."""
    status_code = 404
    default_detail = {
        "error": "card_not_found",
        "message": "The requested card was not found.",
    }
    default_code = 'card_not_found' 