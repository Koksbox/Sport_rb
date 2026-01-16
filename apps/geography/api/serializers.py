# apps/geography/api/serializers.py
from rest_framework import serializers
from apps.geography.models import Region, City, District

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    class Meta:
        model = City
        fields = ['id', 'name', 'region_name']

class DistrictSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = District
        fields = ['id', 'name', 'city_name']