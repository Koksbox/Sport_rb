# apps/analytics/api/serializers.py
from rest_framework import serializers

class AnalyticsReportSerializer(serializers.Serializer):
    title = serializers.CharField()
    data = serializers.DictField()
    generated_at = serializers.DateTimeField()