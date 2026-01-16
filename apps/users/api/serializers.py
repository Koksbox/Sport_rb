# apps/users/api/serializers.py
from rest_framework import serializers
from apps.users.models import UserRole
from apps.geography.models import City, Region

class RoleSelectionSerializer(serializers.Serializer):
    ROLE_CHOICES = ['athlete', 'parent', 'organization']
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    city = serializers.CharField(max_length=100, required=False)  # только для athlete

    def validate(self, attrs):
        user = self.context['request'].user
        if user.roles.exists():
            raise serializers.ValidationError("Вы уже выбрали роль.")
        return attrs

    def save(self):
        user = self.context['request'].user
        role = self.validated_data['role']

        # Создаём только запись о роли
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

        # НЕ СОЗДАЁМ ОРГАНИЗАЦИЮ!
        # Пользователь перейдёт на форму создания
        return user