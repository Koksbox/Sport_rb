# apps/core/context_processors.py
"""
Context processors для добавления данных во все шаблоны
"""
from apps.users.models import UserRole

def active_role(request):
    """Добавляет активную роль пользователя в контекст всех шаблонов"""
    context = {
        'active_role': None,
        'active_role_name': None,
        'active_role_icon': None,
        'active_role_id': None,
    }
    
    if request.user.is_authenticated:
        user = request.user
        
        # Если пользователь - суперпользователь, создаём роль admin_rb, если её нет
        if user.is_superuser:
            admin_role, created = UserRole.objects.get_or_create(
                user=user,
                role='admin_rb',
                defaults={'is_active': True}
            )
            # Устанавливаем admin_rb как активную роль
            request.session['active_role'] = 'admin_rb'
            active_role_value = 'admin_rb'
            active_role_obj = admin_role
        else:
            # Получаем активную роль из сессии
            active_role_value = request.session.get('active_role')
            
            # Если активной роли нет в сессии, берем первую доступную
            if not active_role_value and user.roles.exists():
                first_role = user.roles.filter(is_active=True).first()
                if first_role:
                    active_role_value = first_role.role
                    request.session['active_role'] = active_role_value
                    active_role_obj = first_role
                else:
                    active_role_obj = None
            else:
                # Получаем объект роли
                try:
                    active_role_obj = user.roles.get(role=active_role_value) if active_role_value else None
                except UserRole.DoesNotExist:
                    active_role_obj = None
        
        if active_role_value:
            context['active_role'] = active_role_value
            
            # Название и иконка роли
            role_data = {
                'athlete': {'name': 'Спортсмен', 'icon': '👤'},
                'parent': {'name': 'Родитель', 'icon': '👨‍👩‍👧'},
                'coach': {'name': 'Тренер', 'icon': '🏋️'},
                'organization': {'name': 'Организация', 'icon': '🏢'},
                'director': {'name': 'Директор', 'icon': '🏢'},
                'moderator': {'name': 'Модератор', 'icon': '👮'},
                'admin_rb': {'name': 'Админ РБ', 'icon': '👨‍💼'},
                'committee_staff': {'name': 'Сотрудник спорткомитета', 'icon': '🏛️'},
            }
            
            role_info = role_data.get(active_role_value, {'name': active_role_value.title(), 'icon': '👤'})
            context['active_role_name'] = role_info['name']
            context['active_role_icon'] = role_info['icon']
            
            # Получаем ID роли (unique_id)
            if active_role_obj:
                # Генерируем unique_id, если его нет
                if not active_role_obj.unique_id:
                    import random
                    import string
                    while True:
                        unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        if not UserRole.objects.filter(unique_id=unique_id).exists():
                            active_role_obj.unique_id = unique_id
                            active_role_obj.save(update_fields=['unique_id'])
                            break
                context['active_role_id'] = active_role_obj.unique_id
    
    return context
