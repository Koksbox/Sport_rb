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
    category = serializers.SerializerMethodField()
    age_groups = EventAgeGroupSerializer(many=True, read_only=True)
    organization_name = serializers.SerializerMethodField()
    organizer_name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
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
    
    def get_category(self, obj):
        # Возвращаем первую категорию, если есть связь
        try:
            if hasattr(obj, 'categories') and obj.categories.exists():
                category = obj.categories.first()
                if category:
                    return EventCategorySerializer(category).data
        except Exception as e:
            print(f"Error in get_category: {e}")
            pass
        return None
    
    def get_sport(self, obj):
        # Проверяем наличие категории через related_name или прямое обращение
        try:
            # Если есть связь через EventCategory
            if hasattr(obj, 'categories') and obj.categories.exists():
                category = obj.categories.first()
                if hasattr(category, 'sport') and category.sport:
                    return category.sport.name
        except Exception as e:
            print(f"Error in get_sport: {e}")
            pass
        return None
    
    def get_city(self, obj):
        """Безопасное получение названия города"""
        try:
            if obj.city:
                return obj.city.name
        except Exception as e:
            print(f"Error in get_city: {e}")
        return None
    
    def get_organization_name(self, obj):
        """Безопасное получение названия организации"""
        try:
            if obj.organizer_org:
                return obj.organizer_org.name
        except Exception as e:
            print(f"Error in get_organization_name: {e}")
        return None
    
    def get_organizer_name(self, obj):
        """Безопасное получение имени организатора"""
        try:
            if obj.organizer_user:
                return obj.organizer_user.get_full_name() or obj.organizer_user.email
        except Exception as e:
            print(f"Error in get_organizer_name: {e}")
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
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True, allow_null=True)
    coach_name = serializers.CharField(source='coach.user.get_full_name', read_only=True, allow_null=True)
    athlete_age = serializers.SerializerMethodField()
    athlete_sport = serializers.SerializerMethodField()
    athlete_role_id = serializers.SerializerMethodField()
    coach_role_id = serializers.SerializerMethodField()

    class Meta:
        model = EventRegistration
        fields = ['id', 'registration_type', 'athlete', 'athlete_name', 'athlete_role_id', 
                  'coach', 'coach_name', 'coach_role_id', 'athlete_age', 'athlete_sport', 
                  'status', 'created_at', 'invitation']
    
    def get_athlete_role_id(self, obj):
        """Получить ID роли спортсмена"""
        if obj.athlete:
            try:
                role = obj.athlete.user.roles.filter(role='athlete', is_active=True).first()
                return role.unique_id if role and role.unique_id else None
            except:
                return None
        return None
    
    def get_coach_role_id(self, obj):
        """Получить ID роли тренера"""
        if obj.coach:
            try:
                role = obj.coach.user.roles.filter(role='coach', is_active=True).first()
                return role.unique_id if role and role.unique_id else None
            except:
                return None
        return None
    
    def get_athlete_age(self, obj):
        if obj.athlete and obj.athlete.user.birth_date:
            from django.utils import timezone
            age = timezone.now().year - obj.athlete.user.birth_date.year
            if timezone.now().month < obj.athlete.user.birth_date.month or \
               (timezone.now().month == obj.athlete.user.birth_date.month and timezone.now().day < obj.athlete.user.birth_date.day):
                age -= 1
            return age
        return None
    
    def get_athlete_sport(self, obj):
        if obj.athlete and obj.athlete.main_sport:
            return obj.athlete.main_sport.name
        return None

class EventResultSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True)

    class Meta:
        model = EventResult
        fields = ['id', 'athlete', 'athlete_name', 'place', 'result_value', 'notes']