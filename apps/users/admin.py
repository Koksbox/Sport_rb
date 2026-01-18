# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser, UserRole, Consent, DeletionRequest


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'phone', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    """Форма изменения пользователя"""
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Админка для пользователей"""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'phone', 'last_name', 'first_name', 'patronymic', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'phone', 'last_name', 'first_name', 'patronymic')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        (_('Личная информация'), {
            'fields': ('last_name', 'first_name', 'patronymic', 'birth_date', 'gender', 'city')
        }),
        (_('Социальные сети'), {
            'fields': ('telegram_id', 'vk_id'),
            'classes': ('collapse',)
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'last_name', 'patronymic', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Админка для ролей пользователей"""
    list_display = ('user', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'role')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    """Админка для согласий пользователей"""
    list_display = ('user', 'type', 'granted', 'created_at')
    list_filter = ('type', 'granted', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'type')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeletionRequest)
class DeletionRequestAdmin(admin.ModelAdmin):
    """Админка для запросов на удаление"""
    list_display = ('user', 'processed', 'reason', 'created_at')
    list_filter = ('processed', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'reason')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
