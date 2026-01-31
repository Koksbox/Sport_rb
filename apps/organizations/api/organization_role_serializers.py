# apps/organizations/api/organization_role_serializers.py
from rest_framework import serializers
from apps.organizations.models.organization_role_request import OrganizationRoleRequest

class OrganizationRoleRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = OrganizationRoleRequest
        fields = [
            'id', 'user', 'user_name', 'user_email', 'status', 'message',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at']

class OrganizationRoleRequestCreateSerializer(serializers.Serializer):
    """Сериализатор для создания заявки на роль организации"""
    message = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Проверяем, есть ли уже одобренная заявка
        existing_approved = OrganizationRoleRequest.objects.filter(
            user=user,
            status='approved'
        ).exists()
        
        if existing_approved:
            # Проверяем, есть ли уже роль организации
            if user.roles.filter(role='director').exists():
                raise serializers.ValidationError('У вас уже есть роль организации')
            else:
                # Если заявка одобрена, но роли нет, создаем её
                from apps.users.models import UserRole
                UserRole.objects.get_or_create(user=user, role='director')
                raise serializers.ValidationError('Ваша заявка уже одобрена. Роль организации создана.')
        
        # Проверяем, есть ли уже активная заявка
        existing_pending = OrganizationRoleRequest.objects.filter(
            user=user,
            status='pending'
        ).exists()
        
        if existing_pending:
            raise serializers.ValidationError('У вас уже есть активная заявка на роль организации')
        
        return attrs
    
    def save(self):
        user = self.context['request'].user
        message = self.validated_data.get('message', '')
        
        request = OrganizationRoleRequest.objects.create(
            user=user,
            message=message
        )
        
        return request

class OrganizationRoleRequestReviewSerializer(serializers.Serializer):
    """Сериализатор для рассмотрения заявки администратором"""
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, attrs):
        if attrs['status'] == 'rejected' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({'rejection_reason': 'Укажите причину отклонения'})
        return attrs
