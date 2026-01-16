# apps/city_committee/api/serializers.py
from rest_framework import serializers
from apps.organizations.models import Organization
from apps.geography.models import City

class OrganizationMapSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    region_name = serializers.CharField(source='city.region.name', read_only=True)
    sport_types = serializers.SerializerMethodField()
    accessibility = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'city_name', 'region_name',
            'address', 'latitude', 'longitude', 'sport_types',
            'accessibility'
        ]

    def get_sport_types(self, obj):
        return [sd.sport.name for sd in obj.sport_directions.all()]

    def get_accessibility(self, obj):
        try:
            acc = obj.accessibility
            return {
                'wheelchair_access': acc.wheelchair_access,
                'adapted_restroom': acc.adapted_restroom,
                'sign_language_support': acc.sign_language_support
            }
        except:
            return None

class CityOverviewSerializer(serializers.Serializer):
    total_athletes = serializers.IntegerField()
    athletes_by_age = serializers.DictField()
    active_sections = serializers.IntegerField()
    top_sports = serializers.ListField(child=serializers.DictField())
    coverage_percentage = serializers.FloatField()