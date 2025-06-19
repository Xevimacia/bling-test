from .models import Card
from users.models import CustomUser
from providers.clients.bank_provider import BankProviderClient
from django.db import transaction

class CardService:
    """
    Service layer for card-related business logic. Handles creation, retrieval, and integration with external providers.
    """
    @staticmethod
    def create_card(user: CustomUser, color: str):
        """
        Create a new card for the given user with the specified color.
        Validates input, calls the external provider, and handles errors safely.
        Saves the card in the database transactionally.
        """
        # Input validation
        if color not in ["black", "pink"]:
            raise ValueError("Invalid card color.")

        provider_client = BankProviderClient()
        try:
            provider_response = provider_client.create_card(user.external_id, color)
        except Exception as exc:
            # logger.error(f"Provider error during card creation: {exc}")
            raise RuntimeError("Failed to create card with provider.")

        # Transactional DB save
        try:
            with transaction.atomic():
                card = Card.objects.create(
                    user=user,
                    color=color,
                    external_id=provider_response.get("id"),
                    expiration_date=provider_response.get("expiration_date"),
                    status=provider_response.get("status", Card._meta.get_field('status').get_default()),
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