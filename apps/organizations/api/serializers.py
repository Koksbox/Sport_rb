# apps/organizations/api/serializers.py
from rest_framework import serializers
from apps.organizations.models import Organization

class OrganizationModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'status']
        read_only_fields = ['name', 'inn']

    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Статус должен быть 'approved' или 'rejected'")
        return value


