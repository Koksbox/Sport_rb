# apps/core/context_processors.py
"""
Context processors для добавления данных во все шаблоны
"""

def active_role(request):
    """Добавляет активную роль пользователя в контекст всех шаблонов"""
    context = {
        'active_role': None,
        'active_role_name': None,
        'active_role_icon': None,
    }
    
    if request.user.is_authenticated:
        # Получаем активную роль из сессии
        active_role_value = request.session.get('active_role')
        
        # Если активной роли нет в сессии, берем первую доступную
        if not active_role_value and request.user.roles.exists():
            active_role_value = request.user.roles.first().role
            request.session['active_role'] = active_role_value
        
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
                'committee': {'name': 'Сотрудник спорткомитета', 'icon': '🏛️'},
            }
            
            role_info = role_data.get(active_role_value, {'name': active_role_value.title(), 'icon': '👤'})
            context['active_role_name'] = role_info['name']
            context['active_role_icon'] = role_info['icon']
    
    return context
