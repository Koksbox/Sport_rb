# apps/sports/api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SportSerializer, SportCategorySerializer
from apps.sports.models import Sport, SportCategory

@api_view(['GET'])
def list_sports(request):
    """Список всех видов спорта"""
    sports = Sport.objects.prefetch_related('categories').all()
    return Response(SportSerializer(sports, many=True).data)

@api_view(['GET'])
def list_categories(request, sport_id):
    """Категории для конкретного вида спорта"""
    try:
        sport = Sport.objects.get(id=sport_id)
        categories = sport.categories.all()
        return Response(SportCategorySerializer(categories, many=True).data)
    except Sport.DoesNotExist:
        return Response({"error": "Вид спорта не найден"}, status=404)