# apps/core/api/serializers.py
from rest_framework import serializers
from apps.users.models import Consent

class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ['id', 'type', 'granted', 'granted_at']

class ConsentCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[
        ('fz152_personal', 'Персональные данные'),
        ('fz152_marketing', 'Маркетинг'),
        ('fz152_processing', 'Обработка данных'),
    ])
    granted = serializers.BooleanField()

    def create(self, validated_data):
        user = self.context['request'].user
        consent, created = Consent.objects.update_or_create(
            user=user,
            type=validated_data['type'],
            defaults={'granted': validated_data['granted']}
        )
        return consent