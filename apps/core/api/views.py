# apps/core/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from apps.core.models.news import NewsArticle


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_list(request):
    """Получить список опубликованных новостей (публичный endpoint)"""
    articles = NewsArticle.objects.filter(is_published=True).order_by('-published_at', '-created_at')
    
    data = []
    for article in articles:
        data.append({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'excerpt': article.excerpt,
            'content': article.content,
            'image': article.image.url if article.image else None,
            'author_name': article.author.get_full_name() if article.author else None,
            'published_at': article.published_at,
            'views_count': article.views_count,
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_detail(request, slug):
    """Получить детали новостной статьи по slug (публичный endpoint)"""
    try:
        article = NewsArticle.objects.get(slug=slug, is_published=True)
        # Увеличиваем счётчик просмотров
        article.views_count += 1
        article.save(update_fields=['views_count'])
        
        return Response({
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'content': article.content,
            'excerpt': article.excerpt,
            'image': article.image.url if article.image else None,
            'author_name': article.author.get_full_name() if article.author else None,
            'published_at': article.published_at,
            'views_count': article.views_count,
        })
    except NewsArticle.DoesNotExist:
        return Response({"error": "Статья не найдена"}, status=status.HTTP_404_NOT_FOUND)
