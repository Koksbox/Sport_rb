# apps/notifications/admin.py
from django.contrib import admin
from .models import Notification, NotificationTemplate, NotificationSubscription


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Админка для уведомлений"""
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'recipient__last_name', 'title', 'body')
    raw_id_fields = ('recipient', 'sender')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Админка для шаблонов уведомлений"""
    list_display = ('name', 'channel', 'is_active', 'created_at')
    list_filter = ('channel', 'is_active', 'created_at')
    search_fields = ('name', 'subject_template', 'body_template')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок на уведомления"""
    list_display = ('user', 'subscription_type', 'enabled', 'created_at')
    list_filter = ('subscription_type', 'enabled', 'created_at')
    search_fields = ('user__email', 'user__last_name')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
