# apps/users/api/serializers.py
from rest_framework import serializers
from apps.users.models import UserRole
from apps.geography.models import City


class RoleSelectionSerializer(serializers.Serializer):
    ROLE_CHOICES = ['athlete', 'parent', 'organization']
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    city = serializers.CharField(max_length=100, required=False)  # для спортсмена/организации

    def validate(self, attrs):
        user = self.context['request'].user
        if user.roles.exists():
            raise serializers.ValidationError("Вы уже выбрали роль.")
        return attrs

    def save(self):
        user = self.context['request'].user
        role = self.validated_data['role']

        # 1. Создаём запись UserRole
        UserRole.objects.create(user=user, role=role)

        # 2. Создаём профиль в зависимости от роли
        if role == 'athlete':
            from apps.athletes.models import AthleteProfile
            city_name = self.validated_data.get('city', 'Уфа')
            city, _ = City.objects.get_or_create(name=city_name, defaults={'region_id': 2})  # временно region_id=1
            AthleteProfile.objects.create(user=user, city=city)

        elif role == 'parent':
            from apps.parents.models import ParentProfile
            ParentProfile.objects.create(user=user)

        elif role == 'coach':
            from apps.coaches.models import CoachProfile
            CoachProfile.objects.create(
                user=user,
                city="Уфа",  # временно
                specialization_id=1,  # временно
                experience_years=0
            )

        elif role == 'organization':
            from apps.organizations.models import Organization
            org = Organization.objects.create(
                name=f"Организация {user.email}",
                org_type='private',
                city_id=1,  # временно — позже сделаем выбор
                address="Адрес будет указан позже",
                inn="000000000000",
                created_by=user,  # ← ОБЯЗАТЕЛЬНО!
                status='pending'
            )

            # Роль director будет назначена после модерации — сейчас просто организация создана
            user.organization_created = org  # можно добавить поле или хранить в сессии
        return user
