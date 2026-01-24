# apps/frontend/templatetags/role_names.py
from django import template

register = template.Library()

@register.filter
def role_name(role):
    """Переводит название роли на русский"""
    role_names = {
        'athlete': 'Спортсмен',
        'parent': 'Родитель',
        'coach': 'Тренер',
        'organization': 'Организация',
        'director': 'Директор',
        'moderator': 'Модератор',
        'admin_rb': 'Админ РБ',
        'committee': 'Сотрудник спорткомитета',
    }
    return role_names.get(role, role.title())
