# apps/parents/api/serializers.py
from rest_framework import serializers
from apps.athletes.models import AthleteProfile
from apps.parents.models import ParentChildLink

class ChildProfileSerializer(serializers.ModelSerializer):
    """Только для просмотра — без редактирования"""
    main_sport_name = serializers.CharField(source='main_sport.name', read_only=True, allow_null=True)
    city_name = serializers.CharField(source='city.name', read_only=True, allow_null=True)
    organization_name = serializers.SerializerMethodField()
    coach_names = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    role_unique_id = serializers.SerializerMethodField()

    class Meta:
        model = AthleteProfile
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'full_name', 'birth_date',
            'main_sport_name', 'city_name', 'organization_name', 'coach_names',
            'health_group', 'goals', 'role_unique_id'
        ]
        read_only_fields = '__all__'

    def get_organization_name(self, obj):
        # Получаем организацию через группы, в которые записан спортсмен
        groups = obj.enrollments.filter(status='active').select_related('group__organization')
        orgs = {g.group.organization.name for g in groups if g.group.organization}
        return list(orgs) if orgs else []

    def get_coach_names(self, obj):
        # Тренеры из тех же групп
        try:
            groups = obj.enrollments.filter(status='active').select_related('group')
            coaches = set()
            for enrollment in groups:
                memberships = enrollment.group.coach_memberships.filter(status='active')
                for m in memberships:
                    coaches.add(f"{m.coach.user.first_name} {m.coach.user.last_name}")
            return list(coaches)
        except Exception:
            return []
    
    def get_full_name(self, obj):
        """Получить полное имя из user"""
        if obj.user:
            return obj.user.get_full_name() or f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip() or "Не указано"
        return "Не указано"
    
    def get_role_unique_id(self, obj):
        """Получить уникальный ID роли спортсмена"""
        from apps.users.models import UserRole
        try:
            role = UserRole.objects.get(user=obj.user, role='athlete')
            # Генерируем unique_id, если его нет
            if not role.unique_id:
                import random
                import string
                while True:
                    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not UserRole.objects.filter(unique_id=unique_id).exists():
                        role.unique_id = unique_id
                        role.save()
                        break
            return role.unique_id
        except UserRole.DoesNotExist:
            return None

class ChildLinkRequestSerializer(serializers.Serializer):
    """Запрос на связь родитель-ребёнок по уникальному ID роли"""
    role_unique_id = serializers.CharField(max_length=12, help_text="Уникальный ID роли спортсмена")

    def validate_role_unique_id(self, value):
        from apps.users.models import UserRole
        try:
            user_role = UserRole.objects.get(unique_id=value, role='athlete', is_active=True)
            athlete_profile = user_role.user.athlete_profile
            self.context['athlete'] = athlete_profile
            self.context['user_role'] = user_role
            return value
        except UserRole.DoesNotExist:
            raise serializers.ValidationError("Спортсмен с таким ID не найден или роль неактивна.")

    def save(self):
        parent = self.context['request'].user
        athlete = self.context['athlete']
        
        # Проверяем, не существует ли уже связь
        link, created = ParentChildLink.objects.get_or_create(
            parent=parent,
            child_profile=athlete,
            defaults={
                'status': 'pending_child',
                'requested_by': 'parent'
            }
        )
        
        # Если связь уже существует, обновляем статус
        if not created:
            if link.status == 'rejected':
                link.status = 'pending_child'
                link.requested_by = 'parent'
                link.save()
        
        # Автоматически создаём роль родителя, если её нет
        from apps.users.models import UserRole
        UserRole.objects.get_or_create(user=parent, role='parent')
        
        # Создаём профиль родителя, если его нет
        from apps.parents.models import ParentProfile
        ParentProfile.objects.get_or_create(user=parent)
        
        return link