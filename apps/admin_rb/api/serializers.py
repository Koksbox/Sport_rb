# apps/admin_rb/api/serializers.py
from rest_framework import serializers
from apps.users.models import CustomUser, UserRole

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'city']

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=['moderator', 'admin_rb'])

    def validate_user_id(self, value):
        try:
            user = CustomUser.objects.get(id=value)
            self.context['user'] = user
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

    def save(self):
        user = self.context['user']
        role = self.validated_data['role']
        UserRole.objects.get_or_create(user=user, role=role)
        return user