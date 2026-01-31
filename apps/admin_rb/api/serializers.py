# apps/admin_rb/api/serializers.py
from rest_framework import serializers
from apps.users.models import CustomUser
from apps.users.models import UserRole
from apps.core.models.news import NewsArticle


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'city']


class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=['moderator', 'admin_rb', 'committee_staff'])
    city_name = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='Город для роли committee_staff')
    department = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='Отдел/подразделение')
    position = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='Должность')
    registration_code = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text='Код регистрации (альтернатива ручному вводу)')
    
    def validate(self, attrs):
        role = attrs.get('role')
        registration_code = attrs.get('registration_code', '').strip().upper()
        city_name = attrs.get('city_name', '').strip()
        
        if role == 'committee_staff':
            # Если передан код регистрации, проверяем его
            if registration_code:
                from apps.city_committee.models import CommitteeRegistrationCode
                try:
                    code_obj = CommitteeRegistrationCode.objects.get(
                        code=registration_code,
                        is_active=True
                    )
                    # Если код уже использован другим пользователем, проверяем
                    if code_obj.is_used and code_obj.used_by_email:
                        # Разрешаем использовать код, если он был использован этим же пользователем
                        user_id = attrs.get('user_id')
                        try:
                            from apps.users.models import CustomUser
                            user = CustomUser.objects.get(id=user_id)
                            if code_obj.used_by_email != user.email:
                                raise serializers.ValidationError({
                                    'registration_code': 'Этот код уже использован другим пользователем'
                                })
                        except CustomUser.DoesNotExist:
                            pass
                    
                    # Автоматически заполняем данные из кода
                    if not city_name:
                        attrs['city_name'] = code_obj.city_name
                    if not attrs.get('department'):
                        attrs['department'] = code_obj.department or ''
                    if not attrs.get('position'):
                        attrs['position'] = code_obj.position or ''
                except CommitteeRegistrationCode.DoesNotExist:
                    raise serializers.ValidationError({
                        'registration_code': 'Код регистрации не найден или неактивен'
                    })
            
            # Если код не передан, проверяем обязательность города
            if not registration_code and not city_name:
                raise serializers.ValidationError({
                    'city_name': 'Город обязателен для роли committee_staff (или укажите код регистрации)'
                })
        
        return attrs
    
    def validate_user_id(self, value):
        try:
            user = CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        return value
    
    def save(self):
        user_id = self.validated_data['user_id']
        role = self.validated_data['role']
        user = CustomUser.objects.get(id=user_id)
        
        UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'is_active': True}
        )
        
        # Если роль committee_staff, создаём профиль и обрабатываем код регистрации
        if role == 'committee_staff':
            from apps.city_committee.models import CommitteeStaff, CommitteeRegistrationCode
            from apps.geography.models import City, Region
            from django.utils import timezone
            import random
            import string
            
            registration_code = self.validated_data.get('registration_code', '').strip().upper()
            city_name = self.validated_data.get('city_name', '').strip()
            department = self.validated_data.get('department', '').strip()
            position = self.validated_data.get('position', '').strip()
            
            code_obj = None
            # Если передан код регистрации, используем его данные
            if registration_code:
                try:
                    code_obj = CommitteeRegistrationCode.objects.get(
                        code=registration_code,
                        is_active=True
                    )
                    # Используем данные из кода, если они не указаны вручную
                    if not city_name:
                        city_name = code_obj.city_name
                    if not department:
                        department = code_obj.department or ''
                    if not position:
                        position = code_obj.position or ''
                except CommitteeRegistrationCode.DoesNotExist:
                    pass  # Код уже проверен в validate()
            
            # Получаем или создаём город
            if city_name:
                try:
                    city = City.objects.get(name=city_name)
                except City.DoesNotExist:
                    region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
                    city = City.objects.create(name=city_name, region=region, settlement_type='city')
                
                # Создаём профиль сотрудника спорткомитета
                CommitteeStaff.objects.get_or_create(
                    user=user,
                    defaults={'city': city}
                )
                
                # Если использован существующий код, отмечаем его как использованный
                if code_obj and not code_obj.is_used:
                    code_obj.is_used = True
                    code_obj.used_by_email = user.email
                    code_obj.used_at = timezone.now()
                    code_obj.save()
                elif not code_obj:
                    # Если код не передан, создаём новый код и отмечаем как использованный
                    existing_code = CommitteeRegistrationCode.objects.filter(
                        used_by_email=user.email,
                        is_used=True
                    ).first()
                    
                    if not existing_code:
                        # Генерируем уникальный код
                        while True:
                            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                            if not CommitteeRegistrationCode.objects.filter(code=code).exists():
                                break
                        
                        # Создаём код и сразу отмечаем как использованный
                        CommitteeRegistrationCode.objects.create(
                            code=code,
                            city_name=city_name,
                            department=department,
                            position=position,
                            issued_by='Администратор РБ',
                            is_active=True,
                            is_used=True,
                            used_by_email=user.email,
                            used_at=timezone.now()
                        )
        
        return user


class CommitteeCodeGenerateSerializer(serializers.Serializer):
    """Сериализатор для генерации кодов регистрации спорткомитета"""
    city_name = serializers.CharField(max_length=100, required=True)
    count = serializers.IntegerField(min_value=1, max_value=100, default=1)
    department = serializers.CharField(max_length=255, required=False, allow_blank=True)
    position = serializers.CharField(max_length=255, required=False, allow_blank=True)
    expires_days = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    code_length = serializers.IntegerField(min_value=6, max_value=20, default=8)


class NotificationCreateSerializer(serializers.Serializer):
    """Сериализатор для создания уведомлений"""
    title = serializers.CharField(max_length=255, required=True)
    body = serializers.CharField(required=True)  # Исправлено: TextField -> CharField
    notification_type = serializers.CharField(default='mass_notification')
    
    # Фильтры получателей
    target_all = serializers.BooleanField(default=False, help_text='Отправить всем пользователям')
    target_roles = serializers.ListField(
        child=serializers.ChoiceField(choices=['athlete', 'coach', 'parent', 'director', 'organization', 'committee_staff']),
        required=False,
        help_text='Список ролей для отправки'
    )
    target_event_id = serializers.IntegerField(required=False, help_text='ID мероприятия (отправить участникам)')
    
    def validate(self, attrs):
        if not attrs.get('target_all') and not attrs.get('target_roles') and not attrs.get('target_event_id'):
            raise serializers.ValidationError('Необходимо указать хотя бы один фильтр получателей (target_all, target_roles или target_event_id)')
        return attrs


class NewsArticleSerializer(serializers.ModelSerializer):
    """Сериализатор для новостных статей"""
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'author_email', 'author_name',
            'image', 'is_published', 'published_at', 'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'author', 'published_at', 'views_count', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return None
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
