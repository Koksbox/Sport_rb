#!/usr/bin/env python
"""
Скрипт для тестирования сайта на ошибки
Использование: python test_site.py
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = 'http://127.0.0.1:8060'

def test_endpoint(url, method='GET', data=None, expected_status=200):
    """Тестирует endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        else:
            print(f"❌ Неподдерживаемый метод: {method}")
            return False
        
        status_ok = response.status_code == expected_status
        status_icon = "✅" if status_ok else "❌"
        
        print(f"{status_icon} {method} {url} - Status: {response.status_code} (ожидалось: {expected_status})")
        
        if not status_ok:
            print(f"   Ответ: {response.text[:200]}")
        
        return status_ok
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {url} - Не удалось подключиться (сервер не запущен?)")
        return False
    except Exception as e:
        print(f"❌ {method} {url} - Ошибка: {e}")
        return False

def main():
    print("=" * 60)
    print("Тестирование сайта СпортБаш")
    print("=" * 60)
    print()
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Тестирование API endpoints
    print("📡 Тестирование API endpoints:")
    print("-" * 60)
    
    api_tests = [
        # Auth endpoints
        ('/api/auth/', 'GET', None, 200),
        ('/api/auth/login/', 'POST', {'email': 'test@test.ru', 'password': 'test'}, 400),  # Ожидаем ошибку валидации
        ('/api/auth/register/', 'POST', {'email': 'test@test.ru'}, 400),  # Ожидаем ошибку валидации
        
        # Core endpoints
        ('/api/core/health/', 'GET', None, 200),
        ('/api/core/constants/', 'GET', None, 200),
        
        # Organizations (публичные)
        ('/api/organizations/', 'GET', None, 200),
        
        # Events (публичные)
        ('/api/events/', 'GET', None, 200),
        
        # Geography
        ('/api/geography/regions/', 'GET', None, 200),
        ('/api/geography/cities/', 'GET', None, 200),
        
        # Sports
        ('/api/sports/', 'GET', None, 200),
    ]
    
    for url_path, method, data, expected_status in api_tests:
        url = urljoin(BASE_URL, url_path)
        results['total'] += 1
        if test_endpoint(url, method, data, expected_status):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    print()
    
    # Тестирование Frontend страниц
    print("🌐 Тестирование Frontend страниц:")
    print("-" * 60)
    
    frontend_tests = [
        ('/', 'GET', None, 200),
        ('/login/', 'GET', None, 200),
        ('/register/', 'GET', None, 200),
        ('/organizations/', 'GET', None, 302),  # Редирект на login если не авторизован
        ('/events/', 'GET', None, 302),  # Редирект на login если не авторизован
    ]
    
    for url_path, method, data, expected_status in frontend_tests:
        url = urljoin(BASE_URL, url_path)
        results['total'] += 1
        if test_endpoint(url, method, data, expected_status):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    print()
    print("=" * 60)
    print("Результаты тестирования:")
    print(f"✅ Пройдено: {results['passed']}")
    print(f"❌ Провалено: {results['failed']}")
    print(f"📊 Всего: {results['total']}")
    print(f"📈 Успешность: {results['passed']/results['total']*100:.1f}%")
    print("=" * 60)

if __name__ == '__main__':
    main()
