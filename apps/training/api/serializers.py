# apps/training/api/serializers.py
from rest_framework import serializers
from apps.training.models import TrainingGroup, Schedule, AgeLevel, Enrollment
from apps.sports.models import Sport
from apps.organizations.models import Organization

class AgeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeLevel
        fields = ['id', 'name', 'min_age', 'max_age']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'weekday', 'start_time', 'end_time', 'location']

class TrainingGroupSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    age_level_name = serializers.CharField(source='age_level.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = TrainingGroup
        fields = [
            'id', 'name', 'sport_name', 'age_level_name',
            'organization_name', 'description', 'schedules',
            'enrollments_count'
        ]

    def get_enrollments_count(self, obj):
        return obj.enrollments.filter(status='active').count()

class TrainingGroupCreateSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, required=False)

    class Meta:
        model = TrainingGroup
        fields = [
            'name', 'sport', 'age_level', 'organization',
            'description', 'schedules'
        ]

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        group = TrainingGroup.objects.create(**validated_data)
        for schedule in schedules_data:
            Schedule.objects.create(group=group, **schedule)
        return group