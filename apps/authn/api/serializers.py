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
    """Регистрация без выбора роли - роль выбирается после входа в личном кабинете"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(write_only=True, required=False, help_text="Полное ФИО в формате 'Фамилия Имя Отчество'")
    patronymic = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'patronymic', 'full_name', 'password', 'password2', 'phone', 'city')
        extra_kwargs = {
            'first_name': {'required': False},  # Будет заполняться из full_name
            'last_name': {'required': False},   # Будет заполняться из full_name
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        
        # Если передан full_name, разбиваем его на части
        if 'full_name' in attrs and attrs['full_name']:
            full_name = attrs['full_name'].strip()
            name_parts = [part for part in full_name.split() if part.strip()]
            
            if len(name_parts) < 2:
                raise serializers.ValidationError({"full_name": "Введите полное ФИО: минимум Фамилия и Имя"})
            
            if len(name_parts) > 3:
                raise serializers.ValidationError({"full_name": "ФИО должно содержать не более 3 слов (Фамилия Имя Отчество)"})
            
            # Заполняем отдельные поля
            attrs['last_name'] = name_parts[0]
            attrs['first_name'] = name_parts[1]
            attrs['patronymic'] = name_parts[2] if len(name_parts) > 2 else ''
            del attrs['full_name']
        # Если full_name не передан, но переданы отдельные поля (для обратной совместимости)
        elif not attrs.get('first_name') or not attrs.get('last_name'):
            raise serializers.ValidationError({"full_name": "ФИО обязательно для заполнения"})
        
        return attrs

    def create(self, validated_data):
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        password2 = validated_data.pop('password2', None)
        phone = validated_data.pop('phone', None)
        city = validated_data.pop('city', None)
        patronymic = validated_data.pop('patronymic', '')
        password = validated_data.pop('password')
        
        # Используем транзакцию для атомарности операции
        try:
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    patronymic=patronymic,
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
                
                # НЕ создаем роль - пользователь выберет её в личном кабинете
                # Создаем согласие на обработку ПДн
                from apps.users.models import Consent
                Consent.objects.create(
                    user=user,
                    type='personal_data',
                    granted=True
                )
                
                return user
        except Exception as e:
            logger.error(f'Ошибка при создании пользователя: {str(e)}', exc_info=True)
            raise

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
        email = self.context.get('email')  # Email может быть в контексте

        # Создаём ТОЛЬКО если нет аккаунта с таким vk_id
        user, created = CustomUser.objects.get_or_create(
            vk_id=vk_id,
            defaults={
                'first_name': vk_user.get('first_name', ''),
                'last_name': vk_user.get('last_name', ''),
                'email': email,
            }
        )
        
        # Обновляем данные, если пользователь уже существовал
        if not created:
            updated = False
            if email and not user.email:
                user.email = email
                updated = True
            if vk_user.get('first_name') and not user.first_name:
                user.first_name = vk_user.get('first_name', '')
                updated = True
            if vk_user.get('last_name') and not user.last_name:
                user.last_name = vk_user.get('last_name', '')
                updated = True
            if updated:
                user.save()

        # Привязываем VK-провайдер и создаем согласие (только если новый аккаунт)
        if created:
            AuthProvider.objects.get_or_create(
                user=user,
                provider='vk',
                defaults={'external_id': str(vk_id)}
            )
            # Создаем согласие на обработку ПДн
            from apps.users.models import Consent
            Consent.objects.get_or_create(
                user=user,
                type='personal_data',
                defaults={'granted': True}
            )
        else:
            # Убеждаемся, что провайдер привязан
            AuthProvider.objects.get_or_create(
                user=user,
                provider='vk',
                defaults={'external_id': str(vk_id)}
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
        user_data = tg_user['user']

        # Создаём ТОЛЬКО если нет аккаунта с таким telegram_id
        user, created = CustomUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'email': None,
            }
        )
        
        # Обновляем данные, если пользователь уже существовал
        if not created:
            updated = False
            if user_data.get('first_name') and not user.first_name:
                user.first_name = user_data.get('first_name', '')
                updated = True
            if user_data.get('last_name') and not user.last_name:
                user.last_name = user_data.get('last_name', '')
                updated = True
            if updated:
                user.save()

        # Привязываем Telegram-провайдер и создаем согласие (только если новый аккаунт)
        if created:
            AuthProvider.objects.get_or_create(
                user=user,
                provider='telegram',
                defaults={'external_id': str(telegram_id)}
            )
            # Создаем согласие на обработку ПДн
            from apps.users.models import Consent
            Consent.objects.get_or_create(
                user=user,
                type='personal_data',
                defaults={'granted': True}
            )
        else:
            # Убеждаемся, что провайдер привязан
            AuthProvider.objects.get_or_create(
                user=user,
                provider='telegram',
                defaults={'external_id': str(telegram_id)}
            )
        
        return user