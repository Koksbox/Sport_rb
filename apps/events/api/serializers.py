# apps/events/api/serializers.py
from rest_framework import serializers
from apps.events.models import Event, EventCategory, EventAgeGroup, EventRegistration, EventResult
from apps.athletes.models import AthleteProfile
from apps.organizations.models import Organization

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name']

class EventAgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAgeGroup
        fields = ['id', 'min_age', 'max_age']

class EventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    age_groups = EventAgeGroupSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organizer_org.name', read_only=True, allow_null=True)
    organizer_name = serializers.CharField(source='organizer_user.get_full_name', read_only=True, allow_null=True)
    city = serializers.CharField(source='city.name', read_only=True)
    sport = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='start_date', read_only=True)
    name = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'name', 'description', 'event_type', 'level',
            'city', 'venue', 'start_date', 'end_date', 'date',
            'category', 'age_groups', 'organization_name',
            'organizer_name', 'requires_registration', 'status', 'sport'
        ]
    
    def get_sport(self, obj):
        if obj.category and hasattr(obj.category, 'sport'):
            return obj.category.sport.name if hasattr(obj.category.sport, 'name') else None
        return None

class EventCreateSerializer(serializers.ModelSerializer):
    age_groups = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True,
        required=False
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'level',
            'city', 'venue', 'start_date', 'end_date',
            'organizer_org', 'organizer_user', 'requires_registration',
            'age_groups'
        ]

    def create(self, validated_data):
        age_groups_data = validated_data.pop('age_groups', [])
        event = Event.objects.create(**validated_data)
        for ag in age_groups_data:
            EventAgeGroup.objects.create(event=event, **ag)
        return event

class EventRegistrationSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'athlete', 'athlete_name', 'status']

class EventResultSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True)

    class Meta:
        model = EventResult
        fields = ['id', 'athlete', 'athlete_name', 'place', 'result_value', 'notes']