# apps/core/api/urls.py
from django.urls import path
from .views import get_news_list, get_news_detail

# Импортируем другие views, если они существуют
try:
    from .views import list_consents, update_consent, system_constants, health_check
    from .contact_views import submit_contact
    
    urlpatterns = [
        path('consents/', list_consents, name='core-consents'),
        path('consents/update/', update_consent, name='core-update-consent'),
        path('constants/', system_constants, name='core-constants'),
        path('health/', health_check, name='core-health'),
        path('contact/', submit_contact, name='core-contact'),
        path('news/', get_news_list, name='core-news-list'),
        path('news/<str:slug>/', get_news_detail, name='core-news-detail'),
    ]
except ImportError:
    # Если других views нет, используем только новости
    urlpatterns = [
        path('news/', get_news_list, name='core-news-list'),
        path('news/<str:slug>/', get_news_detail, name='core-news-detail'),
    ]