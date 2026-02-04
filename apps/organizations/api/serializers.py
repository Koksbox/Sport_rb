# apps/organizations/api/serializers.py
from rest_framework import serializers
from apps.organizations.models import Organization, OrganizationDocument
from apps.geography.models import City
from django.utils import timezone


class OrganizationDocumentSerializer(serializers.ModelSerializer):
    file_path = serializers.FileField(required=False)
    
    class Meta:
        model = OrganizationDocument
        fields = ['doc_type', 'file_path']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    documents = OrganizationDocumentSerializer(many=True, required=False)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='city',
        write_only=True,
        required=True
    )
    website = serializers.URLField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    inn = serializers.CharField(max_length=12, required=True)

    class Meta:
        model = Organization
        fields = [
            'name', 'org_type', 'city_id', 'address',
            'latitude', 'longitude', 'website', 'inn',
            'documents'
        ]
    
    def validate_inn(self, value):
        """Валидация ИНН"""
        if not value:
            raise serializers.ValidationError("ИНН обязателен для заполнения")
        
        # Проверяем формат ИНН (10 или 12 цифр)
        if not value.isdigit():
            raise serializers.ValidationError("ИНН должен содержать только цифры")
        
        if len(value) not in [10, 12]:
            raise serializers.ValidationError("ИНН должен содержать 10 или 12 цифр")
        
        # Проверяем уникальность
        if Organization.objects.filter(inn=value).exists():
            raise serializers.ValidationError("Организация с таким ИНН уже существует")
        
        return value
    
    def validate(self, attrs):
        """Дополнительная валидация"""
        # Проверяем, что координаты указаны
        if not attrs.get('latitude') or not attrs.get('longitude'):
            raise serializers.ValidationError({
                'latitude': 'Координаты обязательны для заполнения',
                'longitude': 'Координаты обязательны для заполнения'
            })
        
        return attrs

    def create(self, validated_data):
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        documents_data = validated_data.pop('documents', [])
        
        # Используем транзакцию для атомарности
        try:
            with transaction.atomic():
                organization = Organization.objects.create(
                    created_by=self.context['request'].user,
                    status='pending',
                    **validated_data
                )

                # Сохранение документов
                for doc_data in documents_data:
                    file = doc_data.get('file_path')
                    if file:
                        # Сохраняем файл и получаем путь
                        # Для MVP сохраняем в media/organization_documents/
                        import os
                        from django.core.files.storage import default_storage
                        from django.conf import settings
                        
                        # Генерируем уникальное имя файла
                        file_ext = os.path.splitext(file.name)[1]
                        file_name = f"org_{organization.id}_{doc_data['doc_type']}_{timezone.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
                        file_path = default_storage.save(f'organization_documents/{file_name}', file)
                        
                        OrganizationDocument.objects.create(
                            organization=organization,
                            doc_type=doc_data['doc_type'],
                            file_path=file_path
                        )
            
                return organization
        except Exception as e:
            logger.error(f'Ошибка при создании организации: {str(e)}', exc_info=True)
            raise


class OrganizationListSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='city.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_type', 'city', 'address', 'latitude', 'longitude', 'website', 'sport_directions']
    
    def get_sport_directions(self, obj):
        from apps.organizations.models import SportDirection
        directions = SportDirection.objects.filter(organization=obj)
        return [sd.sport.name for sd in directions]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для организации"""
    city = serializers.CharField(source='city.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    coaches = serializers.SerializerMethodField()
    org_type_display = serializers.CharField(source='get_org_type_display', read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True, required=False, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True, required=False, read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'org_type_display', 'city', 'address',
            'latitude', 'longitude', 'website', 'sport_directions', 'groups', 'coaches'
        ]
    
    def get_sport_directions(self, obj):
        from apps.organizations.models import SportDirection
        directions = SportDirection.objects.filter(organization=obj).select_related('sport')
        return [{'id': sd.id, 'sport_id': sd.sport.id, 'sport_name': sd.sport.name} for sd in directions]
    
    def get_groups(self, obj):
        from apps.training.models import TrainingGroup
        from apps.training.models.schedule import WEEKDAYS
        
        groups = TrainingGroup.objects.filter(organization=obj, is_active=True).select_related('sport', 'age_level').prefetch_related('schedules')
        
        weekday_dict = dict(WEEKDAYS)
        
        return [{
            'id': g.id,
            'name': g.name,
            'sport_id': g.sport.id,
            'sport': g.sport.name,
            'age_level': g.age_level.name if g.age_level else None,
            'description': g.description,
            'schedules': [{
                'weekday': weekday_dict.get(s.weekday, ''),
                'start_time': str(s.start_time),
                'end_time': str(s.end_time),
                'location': s.location
            } for s in g.schedules.all()]
        } for g in groups]
    
    def get_coaches(self, obj):
        from apps.organizations.staff.coach_membership import CoachMembership
        memberships = CoachMembership.objects.filter(
            organization=obj, 
            status='active'
        ).select_related('coach', 'coach__user', 'coach__specialization')
        
        coaches_list = []
        for membership in memberships:
            coach = membership.coach
            coaches_list.append({
                'id': coach.id,
                'full_name': coach.user.get_full_name(),
                'specialization': coach.specialization.name if coach.specialization else None,
                'experience_years': coach.experience_years,
                'bio': coach.bio
            })
        return coaches_list


class OrganizationModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'status']
        read_only_fields = ['name', 'inn']

    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Статус должен быть 'approved' или 'rejected'")
        return value