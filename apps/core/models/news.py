# apps/core/models/news.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser


class NewsArticle(TimeStampedModel):
    """Модель новостной статьи"""
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='URL-адрес')
    content = models.TextField(verbose_name='Содержание')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='Краткое описание')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_articles',
        verbose_name='Автор'
    )
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name='Изображение')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата публикации')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    
    class Meta:
        db_table = 'core_news_article'
        verbose_name = 'Новостная статья'
        verbose_name_plural = 'Новостные статьи'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Автоматически создаём slug из заголовка, если не указан
        if not self.slug and self.title:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            # Убеждаемся, что slug уникален
            base_slug = self.slug
            counter = 1
            while NewsArticle.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Устанавливаем дату публикации при первой публикации
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
