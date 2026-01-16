# apps/city_committee/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from .serializers import OrganizationMapSerializer, CityOverviewSerializer
from apps.organizations.models import Organization
from apps.athletes.models import AthleteProfile
from apps.sports.models import Sport
from apps.events.models import Event

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_city_overview(request):
    """Обзор по городу"""
    # Получаем город пользователя (предполагается, что он привязан к городу)
    committee_staff = request.user.committee_role
    city = committee_staff.city

    # Общее число спортсменов
    total_athletes = AthleteProfile.objects.filter(city=city).count()

    # По возрастам
    current_year = timezone.now().year
    age_groups = {
        '6-10': 0,
        '11-14': 0,
        '15-17': 0,
        '18+': 0
    }
    athletes = AthleteProfile.objects.filter(city=city).select_related('user')
    for athlete in athletes:
        if athlete.user.birth_date:
            age = current_year - athlete.user.birth_date.year
            if 6 <= age <= 10:
                age_groups['6-10'] += 1
            elif 11 <= age <= 14:
                age_groups['11-14'] += 1
            elif 15 <= age <= 17:
                age_groups['15-17'] += 1
            else:
                age_groups['18+'] += 1

    # Активные секции
    active_sections = Organization.objects.filter(
        city=city,
        status='approved'
    ).count()

    # Популярные виды спорта
    top_sports = Sport.objects.annotate(
        athlete_count=Count('main_athletes', filter=Q(main_athletes__city=city))
    ).order_by('-athlete_count')[:5]

    top_sports_data = [
        {'name': sport.name, 'count': sport.athlete_count}
        for sport in top_sports
    ]

    # Процент охвата (условно: от общего числа детей 6-17 в городе)
    # В реальности нужно брать из статистики города, здесь упрощённо
    children_6_17 = sum([age_groups['6-10'], age_groups['11-14'], age_groups['15-17']])
    coverage_percentage = round((children_6_17 / max(children_6_17, 1)) * 100, 2)

    data = {
        'total_athletes': total_athletes,
        'athletes_by_age': age_groups,
        'active_sections': active_sections,
        'top_sports': top_sports_data,
        'coverage_percentage': coverage_percentage
    }

    serializer = CityOverviewSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_map(request):
    """Интерактивная карта организаций"""
    committee_staff = request.user.committee_role
    city = committee_staff.city

    organizations = Organization.objects.filter(
        city=city,
        status='approved'
    ).prefetch_related('sport_directions__sport', 'accessibility')

    serializer = OrganizationMapSerializer(organizations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_gis_data(request):
    """Экспорт в GIS-формат (GeoJSON)"""
    committee_staff = request.user.committee_role
    city = committee_staff.city

    features = []
    organizations = Organization.objects.filter(
        city=city,
        status='approved',
        latitude__isnull=False,
        longitude__isnull=False
    )

    for org in organizations:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(org.longitude), float(org.latitude)]
            },
            "properties": {
                "name": org.name,
                "type": org.org_type,
                "sports": [sd.sport.name for sd in org.sport_directions.all()],
                "accessibility": bool(getattr(org, 'accessibility', None))
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return Response(geojson)