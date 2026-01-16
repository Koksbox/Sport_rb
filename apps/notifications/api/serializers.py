# apps/notifications/api/serializers.py
from rest_framework import serializers
from apps.notifications.models import Notification, NotificationSubscription

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'notification_type', 'is_read', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSubscription
        fields = ['id', 'notification_type', 'channel', 'is_active']