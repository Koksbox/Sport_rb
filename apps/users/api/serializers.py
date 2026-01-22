# apps/users/api/serializers.py
from rest_framework import serializers
from apps.users.models import UserRole, CustomUser
from apps.geography.models import City, Region

class UserBasicSerializer(serializers.ModelSerializer):
    """Сериализатор для основных данных пользователя"""
    photo_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    city_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'full_name', 'email', 'birth_date', 'gender', 'city', 'city_display', 'photo', 'photo_url']
        read_only_fields = ['id', 'email', 'full_name', 'city_display']
        extra_kwargs = {
            'birth_date': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'photo': {'required': False, 'allow_null': True},
            'city': {'required': False, 'allow_blank': True},
        }
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def get_full_name(self, obj):
        """Возвращает полное ФИО в формате 'Фамилия Имя Отчество'"""
        parts = []
        if obj.last_name:
            parts.append(obj.last_name)
        if obj.first_name:
            parts.append(obj.first_name)
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts) if parts else ''
    
    def get_city_display(self, obj):
        """Возвращает город с префиксом (г., с., д.) если он есть в базе"""
        if not obj.city:
            return ''
        try:
            # Пытаемся найти город в базе по имени
            region = Region.objects.get(name="Республика Башкортостан")
            city = City.objects.filter(name=obj.city, region=region).first()
            if city:
                return city.get_display_name()
        except (Region.DoesNotExist, City.DoesNotExist):
            pass
        # Если не нашли, возвращаем как есть
        return obj.city
    
    def validate(self, attrs):
        """Валидация: проверяем, что first_name и last_name заполнены"""
        # Если обновляются отдельные поля, проверяем их
        if 'first_name' in attrs and not attrs['first_name']:
            raise serializers.ValidationError({'first_name': 'Имя обязательно для заполнения'})
        if 'last_name' in attrs and not attrs['last_name']:
            raise serializers.ValidationError({'last_name': 'Фамилия обязательна для заполнения'})
        return attrs

class RoleSelectionSerializer(serializers.Serializer):
    # В свободном доступе только две роли: тренер и спортсмен
    # Роли родителя и директора создаются автоматически при определённых действиях
    ROLE_CHOICES = ['athlete', 'coach']
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    city = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        user = self.context['request'].user
        role = attrs['role']
        
        # Проверяем, есть ли уже эта роль у пользователя
        if user.roles.filter(role=role).exists():
            raise serializers.ValidationError(f"У вас уже есть роль '{role}'.")
        
        return attrs

    def save(self):
        user = self.context['request'].user
        role = self.validated_data['role']

        # Создаем роль (даже если у пользователя уже есть другие роли)
        UserRole.objects.get_or_create(user=user, role=role)

        if role == 'athlete':
            from apps.athletes.models import AthleteProfile
            from apps.sports.models import Sport
            # Используем город из профиля пользователя, если есть
            city_name = self.validated_data.get('city') or user.city or 'Уфа'
            region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
            city, _ = City.objects.get_or_create(name=city_name, region=region)
            # main_sport может быть установлен позже, но нужен для создания профиля
            # Используем первый доступный спорт или создаем временный
            sport = Sport.objects.first()
            if not sport:
                sport = Sport.objects.create(name="Не указан")
            # Создаем профиль только если его еще нет
            AthleteProfile.objects.get_or_create(
                user=user,
                defaults={'city': city, 'main_sport': sport}
            )

        elif role == 'parent':
            from apps.parents.models import ParentProfile
            ParentProfile.objects.get_or_create(user=user)

        elif role == 'coach':
            from apps.coaches.models import CoachProfile
            from apps.sports.models import Sport
            region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
            # Используем город из профиля пользователя, если есть
            city_name = self.validated_data.get('city') or user.city or 'Уфа'
            city, _ = City.objects.get_or_create(name=city_name, region=region)
            # Используем первый доступный спорт или создаем временный
            sport = Sport.objects.first()
            if not sport:
                sport = Sport.objects.create(name="Не указан")
            # Создаем профиль только если его еще нет
            CoachProfile.objects.get_or_create(
                user=user,
                defaults={
                    'city': city,
                    'specialization': sport,
                    'experience_years': 0
                }
            )

        # organization остаётся без создания org
        return user