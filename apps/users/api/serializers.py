# apps/users/api/serializers.py
from rest_framework import serializers
from apps.users.models import UserRole
from apps.geography.models import City, Region

class RoleSelectionSerializer(serializers.Serializer):
    ROLE_CHOICES = ['athlete', 'parent', 'organization', 'coach']  # ← ДОБАВИЛ 'coach'
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    city = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.roles.exists():
            raise serializers.ValidationError("Вы уже выбрали роль.")
        return attrs

    def save(self):
        user = self.context['request'].user
        role = self.validated_data['role']

        UserRole.objects.create(user=user, role=role)

        if role == 'athlete':
            from apps.athletes.models import AthleteProfile
            city_name = self.validated_data.get('city', 'Уфа')
            region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
            city, _ = City.objects.get_or_create(name=city_name, region=region)
            AthleteProfile.objects.create(user=user, city=city)

        elif role == 'parent':
            from apps.parents.models import ParentProfile
            ParentProfile.objects.create(user=user)

        elif role == 'coach':
            from apps.coaches.models import CoachProfile
            region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
            city, _ = City.objects.get_or_create(name="Уфа", region=region)
            CoachProfile.objects.create(
                user=user,
                city=city,
                specialization_id=1,  # временно
                experience_years=0
            )

        # organization остаётся без создания org
        return user