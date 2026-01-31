#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для создания кодов регистрации сотрудников спорткомитета
Использование: python create_committee_codes.py
"""
import os
import sys
import django
import random
import string

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.city_committee.models import CommitteeRegistrationCode

def create_code(city_name, department='', position='', issued_by='Администратор', code_length=8):
    """Создать один код регистрации"""
    # Генерируем уникальный код
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
        if not CommitteeRegistrationCode.objects.filter(code=code).exists():
            break
    
    # Создаём код
    reg_code = CommitteeRegistrationCode.objects.create(
        code=code,
        city_name=city_name,
        department=department,
        position=position,
        issued_by=issued_by,
        is_active=True,
        is_used=False
    )
    
    return reg_code

if __name__ == '__main__':
    print('Создание кодов регистрации для сотрудников спорткомитета...\n')
    
    # Создаём несколько кодов для разных городов
    cities = [
        ('Уфа', 'Спорткомитет', 'Сотрудник'),
        ('Стерлитамак', 'Спорткомитет', 'Сотрудник'),
        ('Нефтекамск', 'Спорткомитет', 'Сотрудник'),
    ]
    
    created_codes = []
    for city_name, department, position in cities:
        code = create_code(city_name, department, position)
        created_codes.append(code)
        print(f'✓ Создан код: {code.code} для города {city_name}')
    
    print(f'\n✓ Всего создано {len(created_codes)} кодов регистрации!\n')
    print('Активные коды регистрации:')
    print('-' * 60)
    active_codes = CommitteeRegistrationCode.objects.filter(is_used=False, is_active=True)
    for code in active_codes:
        print(f'Код: {code.code:10} | Город: {code.city_name:15} | Отдел: {code.department or "-"}')
    print('-' * 60)
