# apps/parents/api/serializers.py
from rest_framework import serializers
from apps.athletes.models import AthleteProfile
from apps.parents.models import ParentChildLink

class ChildProfileSerializer(serializers.ModelSerializer):
    """Только для просмотра — без редактирования"""
    main_sport_name = serializers.CharField(source='main_sport.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    organization_name = serializers.SerializerMethodField()
    coach_names = serializers.SerializerMethodField()

    class Meta:
        model = AthleteProfile
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'birth_date',
            'main_sport_name', 'city_name', 'organization_name', 'coach_names',
            'health_group', 'goals'
        ]
        read_only_fields = '__all__'

    def get_organization_name(self, obj):
        # Получаем организацию через группы, в которые записан спортсмен
        groups = obj.enrollments.filter(status='active').select_related('group__organization')
        orgs = {g.group.organization.name for g in groups if g.group.organization}
        return list(orgs) if orgs else []

    def get_coach_names(self, obj):
        # Тренеры из тех же групп
        groups = obj.enrollments.filter(status='active').select_related('group')
        coaches = set()
        for enrollment in groups:
            memberships = enrollment.group.coach_memberships.filter(status='active')
            for m in memberships:
                coaches.add(f"{m.coach.user.first_name} {m.coach.user.last_name}")
        return list(coaches)

class ChildLinkRequestSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()

    def validate_child_id(self, value):
        try:
            athlete = AthleteProfile.objects.get(id=value)
            self.context['athlete'] = athlete
            return value
        except AthleteProfile.DoesNotExist:
            raise serializers.ValidationError("Спортсмен с таким ID не найден.")

    def save(self):
        parent = self.context['request'].user
        athlete = self.context['athlete']
        link, created = ParentChildLink.objects.get_or_create(
            parent=parent,
            child_profile=athlete,
            defaults={'is_confirmed': False}
        )
        return link