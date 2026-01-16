# apps/notifications/api/urls.py
from django.urls import path
from .views import (
    list_notifications,
    mark_notification_read,
    list_subscriptions,
    update_subscription
)

urlpatterns = [
    path('', list_notifications, name='notifications-list'),
    path('<int:notification_id>/read/', mark_notification_read, name='notification-read'),
    path('subscriptions/', list_subscriptions, name='subscriptions-list'),
    path('subscriptions/<int:subscription_id>/', update_subscription, name='subscription-update'),
]