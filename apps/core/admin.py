# apps/core/admin.py
from django.contrib import admin
from .models.news import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Админка для новостных статей"""
    list_display = ('title', 'author', 'is_published', 'published_at', 'views_count', 'created_at')
    list_filter = ('is_published', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'excerpt', 'author__email', 'author__first_name', 'author__last_name')
    readonly_fields = ('slug', 'views_count', 'created_at', 'updated_at', 'published_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'author', 'image')
        }),
        ('Публикация', {
            'fields': ('is_published', 'published_at')
        }),
        ('Статистика', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если создаётся новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)
