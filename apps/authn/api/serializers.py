# apps/authn/api/serializers.py
from sqlite3 import IntegrityError

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.authn.models import AuthProvider
from apps.users.models import CustomUser
from apps.authn.services.telegram_webapp import validate_telegram_init_data
from django.conf import settings
import requests


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=['athlete', 'parent', 'coach', 'organization'],
        write_only=True,
        required=True,
        help_text='Выберите тип кабинета: athlete (спортсмен), parent (родитель), coach (тренер), organization (организация)'
    )
    phone = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'role', 'phone', 'city')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        password2 = validated_data.pop('password2', None)
        role = validated_data.pop('role')
        phone = validated_data.pop('phone', None)
        city = validated_data.pop('city', None)
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password,
            phone=phone if phone else None,
            city=city if city else ''
        )

        # Привязываем только email-провайдер
        AuthProvider.objects.create(
            user=user,
            provider='email',
            external_id=validated_data['email']
        )
        
        # Создаем роль и профиль сразу
        from apps.users.models import UserRole
        from apps.geography.models import Region, City as CityModel
        from apps.sports.models import Sport
        
        UserRole.objects.create(user=user, role=role)
        
        # Создаем профиль в зависимости от роли
        if role == 'athlete':
            from apps.athletes.models import AthleteProfile
            # Создаем город если указан
            city_obj = None
            if city:
                region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
                city_obj, _ = CityModel.objects.get_or_create(name=city, defaults={'region': region})
            elif CityModel.objects.exists():
                city_obj = CityModel.objects.first()
            
            if city_obj:
                sport = Sport.objects.first()
                if sport:
                    AthleteProfile.objects.create(
                        user=user,
                        city=city_obj,
                        main_sport=sport,
                        health_group='I',
                        goals=['ЗОЖ']
                    )
        
        elif role == 'parent':
            from apps.parents.models import ParentProfile
            ParentProfile.objects.create(user=user)
        
        elif role == 'coach':
            from apps.coaches.models import CoachProfile
            city_obj = None
            if city:
                region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
                city_obj, _ = CityModel.objects.get_or_create(name=city, defaults={'region': region})
            elif CityModel.objects.exists():
                city_obj = CityModel.objects.first()
            
            if city_obj:
                sport = Sport.objects.first()
                if sport:
                    CoachProfile.objects.create(
                        user=user,
                        city=city_obj,
                        specialization=sport,
                        experience_years=0
                    )
        
        # Для organization роль создана, но организация будет создана позже
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['roles'] = list(user.roles.values_list('role', flat=True))
        return token


# apps/authn/api/serializers.py
class VKAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate_access_token(self, value):
        try:
            # Убираем пробелы в URL
            response = requests.get(
                'https://api.vk.com/method/users.get',
                params={
                    'access_token': value,
                    'v': '5.131'
                },
                timeout=10
            )

            if response.status_code != 200:
                raise serializers.ValidationError("Ошибка VK API")

            data = response.json()
            if 'error' in data:
                raise serializers.ValidationError(f"VK Error: {data['error']['error_msg']}")

            user_data = data['response'][0]
            self.context['vk_user'] = user_data
            return value

        except requests.RequestException:
            raise serializers.ValidationError("Не удалось подключиться к VK API")

    def save(self):
        vk_user = self.context['vk_user']
        vk_id = vk_user['id']

        # Создаём ТОЛЬКО если нет аккаунта с таким vk_id
        user, created = CustomUser.objects.get_or_create(
            vk_id=vk_id,
            defaults={
                'first_name': vk_user.get('first_name', ''),
                'last_name': vk_user.get('last_name', ''),
                'email': None,
            }
        )

        # Привязываем VK-провайдер (только если новый аккаунт)
        if created:
            AuthProvider.objects.create(
                user=user,
                provider='vk',
                external_id=str(vk_id)
            )
        return user


class TelegramAuthSerializer(serializers.Serializer):
    init_data = serializers.CharField()

    def validate_init_data(self, value):
        try:
            data = validate_telegram_init_data(value, settings.TELEGRAM_BOT_TOKEN)
            self.context['tg_user'] = data
            return value
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def save(self):
        tg_user = self.context['tg_user']
        telegram_id = int(tg_user['user']['id'])

        # Создаём ТОЛЬКО если нет аккаунта с таким telegram_id
        user, created = CustomUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'first_name': tg_user['user'].get('first_name', ''),
                'last_name': tg_user['user'].get('last_name', ''),
                'email': None,
            }
        )

        # Привязываем Telegram-провайдер (только если новый аккаунт)
        if created:
            AuthProvider.objects.create(
                user=user,
                provider='telegram',
                external_id=str(telegram_id)
            )
        return user