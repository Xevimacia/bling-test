from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Card
from .serializers import CardSerializer
from .services import CardService
from drf_yasg.utils import swagger_auto_schema

class CardViewSet(viewsets.ViewSet):
    """API endpoint that allows cards to be viewed or edited."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get all cards for the authenticated user using the service layer."""
        cards = CardService.list_user_cards(request.user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardSerializer)
    def create(self, request):
        """Create a new card for the authenticated user using the service layer."""
        serializer = CardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        color = serializer.validated_data.get('color')
        external_id = serializer.validated_data.get('external_id')

        try:
            card = CardService.create_card(request.user, color, external_id)
        except ValueError as ve:
            return Response({'detail': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as re:
            return Response({'detail': str(re)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as exc:
            # logger.error(f"Unexpected error during card creation: {exc}")
            return Response({'detail': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        output_serializer = CardSerializer(card)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Get a specific card belonging to the authenticated user using the service layer. Ensures ownership and safe error handling."""
        try:
            card = CardService.retrieve_user_card(request.user, pk)
        except Card.DoesNotExist:
            return Response({'detail': 'Card not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            # Log the error internally (placeholder for actual logging)
            # logger.error(f"Error retrieving card: {exc}")
            return Response({'detail': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = CardSerializer(card)
        return Response(serializer.data)


