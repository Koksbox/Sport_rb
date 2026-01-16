# apps/authn/api/serializers.py
from sqlite3 import IntegrityError

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import CustomUser
from apps.authn.services.telegram_webapp import validate_telegram_init_data
from django.conf import settings
import requests


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')
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
        validated_data.pop('password2')
        try:
            user = CustomUser.objects.create_user(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                password=validated_data['password']
            )
        except IntegrityError:
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['roles'] = list(user.roles.values_list('role', flat=True))
        return token


class VKAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate_access_token(self, value):
        # Проверяем токен через VK API
        response = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': value,
                'v': '5.131'
            }
        )
        if response.status_code != 200 or 'error' in response.json():
            raise serializers.ValidationError("Неверный VK access_token")

        user_data = response.json()['response'][0]
        self.context['vk_user'] = user_data
        return value

    def save(self):
        vk_user = self.context['vk_user']
        vk_id = vk_user['id']

        # Ищем или создаём пользователя
        user, created = CustomUser.objects.get_or_create(
            vk_id=vk_id,
            defaults={
                'first_name': vk_user.get('first_name', ''),
                'last_name': vk_user.get('last_name', ''),
                'email': None,  # будет запрошен позже
            }
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
        first_name = tg_user['user'].get('first_name', '')
        last_name = tg_user['user'].get('last_name', '')

        user, created = CustomUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': None,
            }
        )
        return user