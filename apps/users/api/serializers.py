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
    # Роль родителя создается автоматически при добавлении ребёнка
    # Роль организации даётся только после одобрения заявки
    ROLE_CHOICES = ['athlete', 'coach']
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    
    # Данные для роли спортсмена
    city = serializers.CharField(max_length=100, required=False)
    sport_id = serializers.IntegerField(required=False, help_text='ID вида спорта')
    birth_date = serializers.DateField(required=False, help_text='Дата рождения для спортсмена')
    
    # Данные для роли тренера
    specialization_id = serializers.IntegerField(required=False, help_text='ID специализации (вида спорта) для тренера')
    experience_years = serializers.IntegerField(required=False, min_value=0, help_text='Опыт работы в годах')
    city_coach = serializers.CharField(max_length=100, required=False, help_text='Город для тренера')

    def validate(self, attrs):
        user = self.context['request'].user
        role = attrs['role']
        
        # Проверяем, есть ли уже эта роль у пользователя
        if user.roles.filter(role=role).exists():
            raise serializers.ValidationError(f"У вас уже есть роль '{role}'.")
        
        # Валидация данных в зависимости от роли
        if role == 'athlete':
            sport_id = attrs.get('sport_id')
            if sport_id is None or sport_id == 0:
                raise serializers.ValidationError({'sport_id': ['Необходимо указать вид спорта']})
        elif role == 'coach':
            specialization_id = attrs.get('specialization_id')
            if specialization_id is None or specialization_id == 0:
                raise serializers.ValidationError({'specialization_id': ['Необходимо указать специализацию']})
            if attrs.get('experience_years') is None:
                raise serializers.ValidationError({'experience_years': ['Необходимо указать опыт работы']})
        
        return attrs

    def save(self):
        import logging
        from django.db import transaction
        
        logger = logging.getLogger(__name__)
        
        user = self.context['request'].user
        role = self.validated_data['role']

        # Используем транзакцию для атомарности операции
        try:
            with transaction.atomic():
                # Создаем роль
                user_role, created = UserRole.objects.get_or_create(user=user, role=role)
                
                if not created and not user_role.is_active:
                    # Активируем роль, если она была неактивна
                    user_role.is_active = True
                    user_role.save()

                if role == 'athlete':
                    from apps.athletes.models import AthleteProfile
                    from apps.sports.models import Sport
                    
                    # Получаем или создаем город
                    city_name = self.validated_data.get('city') or user.city or 'Уфа'
                    if not city_name or not city_name.strip():
                        raise serializers.ValidationError({'city': ['Необходимо указать город']})
                    
                    region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
                    city, _ = City.objects.get_or_create(name=city_name.strip(), region=region)
                    
                    # Получаем вид спорта (должен быть обязательно после валидации)
                    sport_id = self.validated_data.get('sport_id')
                    if not sport_id:
                        raise serializers.ValidationError({'sport_id': ['Необходимо указать вид спорта']})
                    
                    try:
                        sport = Sport.objects.get(id=sport_id)
                    except Sport.DoesNotExist:
                        raise serializers.ValidationError({'sport_id': ['Вид спорта не найден']})
                    
                    # Обновляем дату рождения пользователя, если она была указана
                    birth_date = self.validated_data.get('birth_date')
                    if birth_date and not user.birth_date:
                        user.birth_date = birth_date
                        user.save(update_fields=['birth_date'])
                    
                    # Обновляем город пользователя, если он не указан
                    if not user.city:
                        user.city = city_name.strip()
                        user.save(update_fields=['city'])
                    
                    # Создаем профиль спортсмена
                    athlete_profile, profile_created = AthleteProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'city': city, 
                            'main_sport': sport
                        }
                    )
                    
                    # Если профиль уже существовал, обновляем его
                    if not profile_created:
                        athlete_profile.city = city
                        athlete_profile.main_sport = sport
                        athlete_profile.save(update_fields=['city', 'main_sport'])

                elif role == 'coach':
                    from apps.coaches.models import CoachProfile
                    from apps.sports.models import Sport
                    
                    # Получаем или создаем город
                    city_name = self.validated_data.get('city_coach') or user.city or 'Уфа'
                    if not city_name or not city_name.strip():
                        raise serializers.ValidationError({'city_coach': ['Необходимо указать город']})
                    
                    region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
                    city, _ = City.objects.get_or_create(name=city_name.strip(), region=region)
                    
                    # Получаем специализацию
                    specialization_id = self.validated_data.get('specialization_id')
                    if not specialization_id:
                        raise serializers.ValidationError({'specialization_id': ['Необходимо указать специализацию']})
                    
                    try:
                        specialization = Sport.objects.get(id=specialization_id)
                    except Sport.DoesNotExist:
                        raise serializers.ValidationError({'specialization_id': ['Специализация не найдена']})
                    
                    # Обновляем город пользователя, если он не указан
                    if not user.city:
                        user.city = city_name.strip()
                        user.save(update_fields=['city'])
                    
                    # Создаем профиль тренера
                    coach_profile, coach_profile_created = CoachProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'city': city,
                            'specialization': specialization,
                            'experience_years': self.validated_data.get('experience_years', 0)
                        }
                    )
                    
                    # Обновляем данные, если профиль уже существовал
                    if not coach_profile_created:
                        coach_profile.city = city
                        coach_profile.specialization = specialization
                        coach_profile.experience_years = self.validated_data.get('experience_years', coach_profile.experience_years)
                        coach_profile.save(update_fields=['city', 'specialization', 'experience_years'])
                        
        except Exception as e:
                logger.error(f'Ошибка при создании профиля для роли {role}: {str(e)}', exc_info=True)
                # Откатываем создание роли, если была ошибка
                if created:
                    user_role.delete()
                # Пробрасываем ValidationError как есть, другие ошибки оборачиваем
                if isinstance(e, serializers.ValidationError):
                    raise
                raise serializers.ValidationError({'error': [f'Ошибка при создании профиля: {str(e)}']})

        return user
