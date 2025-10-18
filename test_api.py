#!/usr/bin/env python3
"""
Тест для проверки работы API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("Тестирование API...")
    
    # Тест главной страницы
    print("\n1. Тест главной страницы:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Статус: {response.status_code}")
        print(f"Тип контента: {response.headers.get('content-type', 'Неизвестно')}")
        if response.status_code == 200:
            print("OK: Главная страница работает")
        else:
            print("ERROR: Главная страница не работает")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Тест API документации
    print("\n2. Тест API документации:")
    try:
        response = requests.get(f"{base_url}/api/docs")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print("OK: API документация доступна")
        else:
            print("ERROR: API документация недоступна")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Тест API организаций
    print("\n3. Тест API организаций:")
    try:
        response = requests.get(f"{base_url}/api/organizations")
        print(f"Статус: {response.status_code}")
        print(f"Тип контента: {response.headers.get('content-type', 'Неизвестно')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK: API организаций работает")
            print(f"Количество записей: {data.get('total', 'Неизвестно')}")
            print(f"Страниц: {data.get('pages', 'Неизвестно')}")
        elif response.status_code == 404:
            print("ERROR: API организаций возвращает 404")
        else:
            print(f"ERROR: API организаций возвращает статус {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Тест других API эндпоинтов
    endpoints = [
        "/api/financial-indicators",
        "/api/taxes", 
        "/api/contacts",
        "/api/addresses"
    ]
    
    print("\n4. Тест других API эндпоинтов:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    test_api()
