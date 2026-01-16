# apps/notifications/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import NotificationSerializer, SubscriptionSerializer
from apps.notifications.models import Notification, NotificationSubscription

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """Список уведомлений пользователя"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return Response(NotificationSerializer(notifications, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Уведомление прочитано"})
    except Notification.DoesNotExist:
        return Response({"error": "Уведомление не найдено"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_subscriptions(request):
    """Список подписок пользователя"""
    subscriptions = NotificationSubscription.objects.filter(user=request.user)
    return Response(SubscriptionSerializer(subscriptions, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_subscription(request, subscription_id):
    """Обновить подписку"""
    try:
        subscription = NotificationSubscription.objects.get(id=subscription_id, user=request.user)
        serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except NotificationSubscription.DoesNotExist:
        return Response({"error": "Подписка не найдена"}, status=404)