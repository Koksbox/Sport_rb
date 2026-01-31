# apps/coaches/api/serializers.py
from rest_framework import serializers

from apps.organizations.models import Organization
from apps.training.models import TrainingGroup, Enrollment, AgeLevel
from apps.athletes.models import AthleteProfile, MedicalInfo
from apps.sports.models import Sport
from apps.coaches.models import ClubRequest, CoachProfile, CoachInvitation


class AthleteMedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInfo
        fields = ['conditions', 'other_conditions', 'allergies']


class AthleteForCoachSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    birth_date = serializers.DateField(source='user.birth_date', read_only=True)
    main_sport = serializers.CharField(source='main_sport.name', read_only=True)
    medical_info = serializers.SerializerMethodField()
    role_id = serializers.SerializerMethodField()

    class Meta:
        model = AthleteProfile
        fields = [
            'id', 'full_name', 'birth_date', 'main_sport',
            'health_group', 'goals', 'medical_info', 'role_id'
        ]
    
    def get_role_id(self, obj):
        """Получить ID роли спортсмена"""
        try:
            role = obj.user.roles.filter(role='athlete', is_active=True).first()
            return role.unique_id if role and role.unique_id else None
        except:
            return None

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


class CoachProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля тренера"""
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    city_id = serializers.IntegerField(source='city.id', read_only=True)
    specialization_id = serializers.IntegerField(source='specialization.id', read_only=True)
    
    class Meta:
        model = CoachProfile
        fields = [
            'id', 'city', 'city_id', 'city_name', 'phone', 'telegram', 
            'specialization', 'specialization_id', 'specialization_name', 'experience_years', 'education'
        ]
        extra_kwargs = {
            'city': {'required': False},
            'specialization': {'required': False},
        }
    
    def to_internal_value(self, data):
        """Преобразуем city_id и specialization_id в объекты"""
        # Сохраняем оригинальные данные
        if 'city_id' in data:
            from apps.geography.models import City
            try:
                city = City.objects.get(id=data['city_id'])
                data['city'] = city.id
            except (City.DoesNotExist, ValueError, TypeError):
                pass
        if 'specialization_id' in data:
            from apps.sports.models import Sport
            try:
                sport = Sport.objects.get(id=data['specialization_id'])
                data['specialization'] = sport.id
            except (Sport.DoesNotExist, ValueError, TypeError):
                pass
        return super().to_internal_value(data)


class CoachInvitationSerializer(serializers.ModelSerializer):
    """Сериализатор для приглашений тренеров"""
    coach_name = serializers.CharField(source='coach.user.get_full_name', read_only=True)
    coach_email = serializers.CharField(source='coach.user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True, allow_null=True)
    age_levels = serializers.PrimaryKeyRelatedField(
        queryset=AgeLevel.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = CoachInvitation
        fields = [
            'id', 'coach', 'coach_name', 'coach_email', 'organization', 'organization_name',
            'specialization', 'specialization_name', 'age_levels', 'message', 'status',
            'created_at', 'responded_at'
        ]
        read_only_fields = ['status', 'responded_at']


class CoachInvitationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания приглашения"""
    age_levels = serializers.PrimaryKeyRelatedField(
        queryset=AgeLevel.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = CoachInvitation
        fields = ['coach', 'specialization', 'age_levels', 'message']

    def validate(self, attrs):
        # Проверяем, что директор может приглашать в свою организацию
        request = self.context['request']
        if not hasattr(request.user, 'director_role'):
            raise serializers.ValidationError("Только директор может отправлять приглашения")
        
        director = request.user.director_role
        organization = director.organization
        
        # Проверяем, что тренер еще не работает в этой организации
        from apps.organizations.staff.coach_membership import CoachMembership
        if CoachMembership.objects.filter(
            coach=attrs['coach'],
            organization=organization,
            status='active'
        ).exists():
            raise serializers.ValidationError("Тренер уже работает в этой организации")
        
        # Проверяем, что нет активного приглашения
        if CoachInvitation.objects.filter(
            coach=attrs['coach'],
            organization=organization,
            status='pending'
        ).exists():
            raise serializers.ValidationError("Приглашение уже отправлено этому тренеру")
        
        attrs['organization'] = organization
        return attrs


class FreeOrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор для свободных организаций (где тренер может подать заявку)"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()
    has_pending_request = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'city_name', 'address', 'website',
            'sport_directions', 'has_pending_request'
        ]

    def get_sport_directions(self, obj):
        return [{'id': sd.sport.id, 'name': sd.sport.name} for sd in obj.sport_directions.all()]

    def get_has_pending_request(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'coach_profile'):
            return False
        coach = request.user.coach_profile
        return ClubRequest.objects.filter(
            coach=coach,
            organization=obj,
            status__in=['pending', 'approved']
        ).exists()


class FreeCoachSerializer(serializers.ModelSerializer):
    """Сериализатор для свободных тренеров"""
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True, allow_null=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    has_pending_invitation = serializers.SerializerMethodField()

    class Meta:
        model = CoachProfile
        fields = [
            'id', 'full_name', 'email', 'specialization_name', 'city_name',
            'experience_years', 'bio', 'has_pending_invitation'
        ]

    def get_has_pending_invitation(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'director_role'):
            return False
        director = request.user.director_role
        organization = director.organization
        return CoachInvitation.objects.filter(
            coach=obj,
            organization=organization,
            status='pending'
        ).exists()


class ClubRequestDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для заявок тренеров"""
    coach_name = serializers.CharField(source='coach.user.get_full_name', read_only=True)
    coach_email = serializers.CharField(source='coach.user.email', read_only=True)
    coach_phone = serializers.CharField(source='coach.phone', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    age_levels = serializers.SerializerMethodField()

    class Meta:
        model = ClubRequest
        fields = [
            'id', 'coach', 'coach_name', 'coach_email', 'coach_phone',
            'organization', 'organization_name', 'specialization', 'specialization_name',
            'age_levels', 'message', 'status', 'rejected_reason', 'created_at'
        ]

    def get_age_levels(self, obj):
        return [{'id': al.id, 'name': al.name} for al in obj.age_levels.all()]