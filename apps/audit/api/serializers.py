# apps/audit/api/serializers.py
from rest_framework import serializers
from apps.audit.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    target_type = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'timestamp', 'actor_name',
            'target_type', 'target_id', 'details'
        ]