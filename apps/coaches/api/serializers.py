# apps/coaches/api/serializers.py
from rest_framework import serializers

from apps.organizations.models import Organization
from apps.training.models import TrainingGroup, Enrollment, AgeLevel
from apps.athletes.models import AthleteProfile, MedicalInfo
from apps.sports.models import Sport
from apps.coaches.models import ClubRequest


class AthleteMedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInfo
        fields = ['conditions', 'other_conditions', 'allergies']


class AthleteForCoachSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    birth_date = serializers.DateField(source='user.birth_date', read_only=True)
    main_sport = serializers.CharField(source='main_sport.name', read_only=True)
    medical_info = serializers.SerializerMethodField()

    class Meta:
        model = AthleteProfile
        fields = [
            'id', 'full_name', 'birth_date', 'main_sport',
            'health_group', 'goals', 'medical_info'
        ]

    def get_medical_info(self, obj):
        # Медицинские данные видны ТОЛЬКО если спортсмен в группе тренера
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'coach_profile'):
            return None

        coach = request.user.coach_profile
        # Проверяем, есть ли пересечение по группам
        athlete_groups = obj.enrollments.filter(status='active').values_list('group_id', flat=True)
        coach_groups = coach.coach_memberships.filter(status='active').values_list('groups__id', flat=True)

        if set(athlete_groups) & set(coach_groups):
            try:
                medical = obj.medical_info
                return AthleteMedicalInfoSerializer(medical).data
            except MedicalInfo.DoesNotExist:
                return None
        return None


class EnrollmentSerializer(serializers.ModelSerializer):
    athlete = AthleteForCoachSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'athlete', 'status', 'joined_at']


class TrainingGroupSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    age_level_name = serializers.CharField(source='age_level.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingGroup
        fields = [
            'id', 'name', 'sport_name', 'age_level_name',
            'organization_name', 'description', 'enrollments'
        ]


class ClubSearchSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    region_name = serializers.CharField(source='city.region.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'city_name', 'region_name',
            'address', 'website', 'sport_directions'
        ]

    def get_sport_directions(self, obj):
        return [sd.sport.name for sd in obj.sport_directions.all()]



class ClubRequestSerializer(serializers.ModelSerializer):
    age_levels = serializers.PrimaryKeyRelatedField(
        queryset=AgeLevel.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = ClubRequest
        fields = ['id', 'organization', 'specialization', 'age_levels', 'message']

    def validate(self, attrs):
        coach = self.context['request'].user.coach_profile
        org = attrs['organization']
        # Проверка: нет активной или ожидающей заявки
        if ClubRequest.objects.filter(
            coach=coach,
            organization=org,
            status__in=['pending', 'approved']
        ).exists():
            raise serializers.ValidationError("Вы уже отправляли заявку в этот клуб.")
        return attrs

    def create(self, validated_data):
        coach = self.context['request'].user.coach_profile
        return ClubRequest.objects.create(coach=coach, **validated_data)