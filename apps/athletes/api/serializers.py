# apps/athletes/api/serializers.py
from rest_framework import serializers
from apps.athletes.models import (
    AthleteProfile, MedicalInfo, EmergencyContact,
    SocialStatus, AthleteSpecialization, SectionEnrollmentRequest
)
from apps.parents.models import ParentChildLink
from apps.sports.models import Sport
from rest_framework import serializers
from apps.organizations.models import Organization

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['full_name', 'phone']

class MedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInfo
        fields = ['conditions', 'other_conditions', 'allergies', 'health_issues_description']

class SocialStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialStatus
        fields = ['status', 'document_path']

class AthleteSpecializationSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = AthleteSpecialization
        fields = ['sport', 'sport_name', 'is_primary']

class AthleteProfileSerializer(serializers.ModelSerializer):
    emergency_contact = EmergencyContactSerializer(required=False)
    medical_info = MedicalInfoSerializer(required=False)
    social_status = SocialStatusSerializer(required=False)
    specializations = AthleteSpecializationSerializer(many=True, read_only=True)
    main_sport_name = serializers.CharField(source='main_sport.name', read_only=True)
    additional_sports = serializers.SerializerMethodField()

    class Meta:
        model = AthleteProfile
        fields = [
            'id', 'city', 'school_or_university', 'main_sport', 'main_sport_name',
            'health_group', 'goals', 'emergency_contact', 'medical_info',
            'social_status', 'specializations', 'additional_sports'
        ]
    
    def get_additional_sports(self, obj):
        """Получить дополнительные виды спорта (не основные)"""
        additional = obj.specializations.filter(is_primary=False)
        return [{'id': s.sport.id, 'name': s.sport.name} for s in additional]

    def update(self, instance, validated_data):
        # Обновление вложенных объектов
        ec_data = validated_data.pop('emergency_contact', None)
        med_data = validated_data.pop('medical_info', None)
        ss_data = validated_data.pop('social_status', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ec_data:
            ec, _ = EmergencyContact.objects.update_or_create(
                athlete=instance, defaults=ec_data
            )
        if med_data:
            med, _ = MedicalInfo.objects.update_or_create(
                athlete=instance, defaults=med_data
            )
        if ss_data:
            ss, _ = SocialStatus.objects.update_or_create(
                athlete=instance, defaults=ss_data
            )

        return instance


class ParentRequestSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    parent_id = serializers.IntegerField(source='parent.id', read_only=True)

    class Meta:
        model = ParentChildLink
        fields = ['id', 'parent_id', 'parent_name', 'created_at']
        read_only_fields = ['id', 'parent_id', 'parent_name', 'created_at']


class ClubForAthleteSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'city_name', 'address',
            'sport_directions', 'groups'
        ]

    def get_sport_directions(self, obj):
        return [sd.sport.name for sd in obj.sport_directions.all()]

    def get_groups(self, obj):
        groups = obj.groups.filter(is_active=True)
        return [{
            'id': g.id,
            'name': g.name,
            'age_level': g.age_level.name,
            'schedule': [{'weekday': s.weekday, 'time': str(s.start_time)} for s in g.schedules.all()]
        } for g in groups]


from apps.training.models import Enrollment

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['group']

    def validate(self, attrs):
        athlete = self.context['request'].user.athlete_profile
        group = attrs['group']
        # Проверка: нет активной или ожидающей заявки
        if Enrollment.objects.filter(
            athlete=athlete,
            group=group,
            status__in=['pending', 'active']
        ).exists():
            raise serializers.ValidationError("Вы уже подали заявку в эту группу.")
        return attrs

    def create(self, validated_data):
        athlete = self.context['request'].user.athlete_profile
        return Enrollment.objects.create(
            athlete=athlete,
            status='pending',
            **validated_data
        )


class SectionEnrollmentRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для заявки на секцию"""
    class Meta:
        model = SectionEnrollmentRequest
        fields = ['sport_direction', 'message']

    def validate(self, attrs):
        athlete = self.context['request'].user.athlete_profile
        sport_direction = attrs['sport_direction']
        
        # Проверка: нет активной или ожидающей заявки на эту секцию
        if SectionEnrollmentRequest.objects.filter(
            athlete=athlete,
            sport_direction=sport_direction,
            status='pending'
        ).exists():
            raise serializers.ValidationError("Вы уже подали заявку на эту секцию.")
        
        return attrs

    def create(self, validated_data):
        athlete = self.context['request'].user.athlete_profile
        sport_direction = validated_data['sport_direction']
        organization = sport_direction.organization
        
        return SectionEnrollmentRequest.objects.create(
            athlete=athlete,
            organization=organization,
            status='pending',
            **validated_data
        )


# apps/athletes/api/serializers.py
from apps.attendance.models import AttendanceRecord
from apps.events.models import EventParticipation, EventResult
from apps.achievements.models import Achievement

class AttendanceProgressSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    status = serializers.CharField()

    class Meta:
        model = AttendanceRecord
        fields = ['date', 'status']

class EventProgressSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title')
    event_date = serializers.DateTimeField(source='event.start_date')
    result = serializers.SerializerMethodField()

    class Meta:
        model = EventParticipation
        fields = ['event_title', 'event_date', 'result']

    def get_result(self, obj):
        try:
            result = obj.event.results.get(athlete=obj.athlete)
            return {
                'place': result.place,
                'value': result.result_value
            }
        except EventResult.DoesNotExist:
            return None

class AchievementProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['title', 'date', 'achievement_type']

class AthleteProgressSerializer(serializers.Serializer):
    attendance = AttendanceProgressSerializer(many=True)
    events = EventProgressSerializer(many=True)
    achievements = AchievementProgressSerializer(many=True)