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
    cities = City.objects.select_related('region').all()
    return Response(CitySerializer(cities, many=True).data)

@api_view(['GET'])
def list_districts(request):
    districts = District.objects.select_related('city__region').all()
    return Response(DistrictSerializer(districts, many=True).data)