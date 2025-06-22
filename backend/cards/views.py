import uuid
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Card
from .serializers import CardSerializer, CardCreateSerializer
from .services import CardService
from .exceptions import ServiceException
from drf_yasg.utils import swagger_auto_schema

class CardViewSet(viewsets.ViewSet):
    """API endpoint that allows cards to be viewed or edited."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get all cards for the authenticated user using the service layer."""
        cards = CardService.list_user_cards(request.user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CardCreateSerializer)
    def create(self, request):
        """Create a new card for the authenticated user using the service layer."""
        serializer = CardCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        color = serializer.validated_data.get('color')

        try:
            card = CardService.create_card(request.user, color)
        except ServiceException as exc:
            trace_id = uuid.uuid4()
            # logger.error(f"Service error [trace_id: {trace_id}]: {exc.detail}")
            error_response = exc.detail
            error_response['trace_id'] = str(trace_id)
            return Response(error_response, status=exc.status_code)
        except Exception as exc:
            trace_id = uuid.uuid4()
            # logger.error(f"Unexpected error [trace_id: {trace_id}]: {exc}")
            return Response({'detail': 'An unexpected error occurred.', 'trace_id': trace_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        output_serializer = CardSerializer(card)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Get a specific card belonging to the authenticated user using the service layer. Ensures ownership and safe error handling."""
        try:
            card = CardService.retrieve_user_card(request.user, pk)
        except ServiceException as exc:
            trace_id = uuid.uuid4()
            # logger.error(f"Service error [trace_id: {trace_id}]: {exc.detail}")
            error_response = exc.detail
            error_response['trace_id'] = str(trace_id)
            return Response(error_response, status=exc.status_code)
        except Exception as exc:
            # Log the error internally (placeholder for actual logging)
            # logger.error(f"Error retrieving card [trace_id: {trace_id}]: {exc}")
            trace_id = uuid.uuid4()
            return Response({'detail': 'An unexpected error occurred.', 'trace_id': trace_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = CardSerializer(card)
        return Response(serializer.data)


