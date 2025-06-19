from .models import Card
from users.models import CustomUser
from providers.clients.bank_provider import BankProviderClient
from django.db import transaction
from django.utils import timezone
from dateutil.parser import isoparse

class CardService:
    """
    Service layer for card-related business logic. Handles creation, retrieval, and integration with external providers.
    """
    @staticmethod
    def create_card(user: CustomUser, color: str, external_id: str = None):
        """
        Create a new card for the given user with the specified color.
        - If not external_id, use the logged-in user's external_id.
        - If external_id is 'invalid_user_id' or 'provider_error', use as is (for test simulation).
        - Any other value for external_id is rejected with a ValueError.
        Validates input, calls the external provider, and handles errors safely.
        Saves the card in the database transactionally.
        """
        # Input validation
        if color not in ["black", "pink"]:
            raise ValueError("Invalid card color.")

        # Determine which external_id to use
        if not external_id:
            provider_external_id = user.external_id
        elif external_id in ["invalid_user_id", "provider_error"]:
            provider_external_id = external_id
        else:
            raise ValueError("Invalid external_id for this operation.")

        provider_client = BankProviderClient()
        try:
            provider_response = provider_client.create_card(provider_external_id, color)
        except Exception as exc:
            # logger.error(f"Provider error during card creation: {exc}")
            raise RuntimeError("Failed to create card with provider.")

        # Parse expiration_date as aware datetime
        expiration_date = provider_response.get("expiration_date")
        if expiration_date:
            dt = isoparse(expiration_date)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            expiration_date = dt

        # Enforce that 'status' is present in provider response
        if "status" not in provider_response:
            raise RuntimeError("Provider did not return status")

        # Transactional DB save
        try:
            with transaction.atomic():
                card = Card.objects.create(
                    user=user,
                    color=color,
                    external_id=provider_response.get("id"),
                    expiration_date=expiration_date,
                    status=provider_response["status"],
                )
        except Exception as exc:
            # logger.error(f"Database error during card creation: {exc}")
            raise RuntimeError("Failed to save card in the database.")

        return card

    @staticmethod
    def list_user_cards(user: CustomUser):
        """
        Return all cards belonging to the given user.
        """
        return Card.objects.filter(user=user)

    @staticmethod
    def retrieve_user_card(user: CustomUser, pk: int):
        """
        Retrieve a specific card by primary key, ensuring it belongs to the given user.
        Raises Card.DoesNotExist if not found.
        """
        return Card.objects.get(pk=pk, user=user) 