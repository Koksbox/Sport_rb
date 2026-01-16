# apps/sports/api/serializers.py
from rest_framework import serializers
from apps.sports.models import Sport, SportCategory

class SportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SportCategory
        fields = ['id', 'name']

class SportSerializer(serializers.ModelSerializer):
    categories = SportCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Sport
        fields = ['id', 'name', 'categories']