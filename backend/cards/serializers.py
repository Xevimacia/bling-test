from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'external_id', 'color', 'expiration_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
