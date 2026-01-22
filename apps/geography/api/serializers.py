# apps/geography/api/serializers.py
from rest_framework import serializers
from apps.geography.models import Region, City, District

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'region_name', 'settlement_type', 'display_name']
    
    def get_display_name(self, obj):
        """Возвращает название с обозначением типа"""
        type_prefix = {
            'city': 'г.',
            'village': 'с.',
            'settlement': 'д.',
            'town': 'п.',
        }.get(obj.settlement_type, '')
        return f"{type_prefix} {obj.name}".strip() if type_prefix else obj.name

class DistrictSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = District
        fields = ['id', 'name', 'city_name']