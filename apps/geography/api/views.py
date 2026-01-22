# apps/geography/api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RegionSerializer, CitySerializer, DistrictSerializer
from apps.geography.models import Region, City, District

@api_view(['GET'])
def list_regions(request):
    regions = Region.objects.all()
    return Response(RegionSerializer(regions, many=True).data)

@api_view(['GET'])
def list_cities(request):
    """Список городов, сёл, деревень Республики Башкортостан"""
    # Фильтруем только города Республики Башкортостан
    try:
        region = Region.objects.get(name="Республика Башкортостан")
        cities = City.objects.filter(region=region).select_related('region').order_by('name')
    except Region.DoesNotExist:
        # Если регион не найден, возвращаем все города
        cities = City.objects.select_related('region').order_by('name')
    
    return Response(CitySerializer(cities, many=True).data)

@api_view(['GET'])
def search_cities(request):
    """Поиск городов для автокомплита"""
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response([])
    
    try:
        region = Region.objects.get(name="Республика Башкортостан")
        cities = City.objects.filter(
            region=region,
            name__icontains=query
        ).select_related('region').order_by('settlement_type', 'name')[:20]
    except Region.DoesNotExist:
        cities = City.objects.filter(
            name__icontains=query
        ).select_related('region').order_by('settlement_type', 'name')[:20]
    
    # Формируем данные с обозначениями типов
    results = []
    for city in cities:
        type_prefix = {
            'city': 'г.',
            'village': 'с.',
            'settlement': 'д.',
            'town': 'п.',
        }.get(city.settlement_type, '')
        display_name = f"{type_prefix} {city.name}".strip() if type_prefix else city.name
        
        results.append({
            'id': city.id,
            'name': city.name,
            'display_name': display_name,
            'settlement_type': city.settlement_type,
        })
    
    return Response(results)

@api_view(['GET'])
def list_districts(request):
    districts = District.objects.select_related('city__region').all()
    return Response(DistrictSerializer(districts, many=True).data)