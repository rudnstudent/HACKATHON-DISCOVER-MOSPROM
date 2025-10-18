#!/usr/bin/env python3
"""
Тест фильтрации API
"""

import requests
import json

def test_api_filters():
    base_url = "http://localhost:5000"
    
    print("=== ТЕСТИРОВАНИЕ ФИЛЬТРАЦИИ API ===\n")
    
    # 1. Базовый запрос без фильтров
    print("1. Базовый запрос организаций:")
    response = requests.get(f"{base_url}/api/organizations")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Всего записей: {data['total']}")
        print(f"   Записей на странице: {len(data['items'])}")
        if data['items']:
            print(f"   Первая запись: {data['items'][0]['name']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 2. Фильтрация по точному значению
    print("\n2. Фильтрация по точному значению (inn=1234567890):")
    response = requests.get(f"{base_url}/api/organizations?inn=1234567890")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        print(f"   Примененные фильтры: {data.get('filters_applied', {})}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 3. Поиск по подстроке
    print("\n3. Поиск по подстроке (name_like=Тест):")
    response = requests.get(f"{base_url}/api/organizations?name_like=Тест")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        print(f"   Примененные фильтры: {data.get('filters_applied', {})}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 4. Общий поиск
    print("\n4. Общий поиск (search=организация):")
    response = requests.get(f"{base_url}/api/organizations?search=организация")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        print(f"   Примененные фильтры: {data.get('filters_applied', {})}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 5. Сортировка
    print("\n5. Сортировка по имени (sort_by=name&sort_order=desc):")
    response = requests.get(f"{base_url}/api/organizations?sort_by=name&sort_order=desc")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        if data['items']:
            print(f"   Первая запись (после сортировки): {data['items'][0]['name']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 6. Фильтрация финансовых показателей по диапазону
    print("\n6. Фильтрация финансовых показателей (revenue_min=500000):")
    response = requests.get(f"{base_url}/api/financial-indicators?revenue_min=500000")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        print(f"   Примененные фильтры: {data.get('filters_applied', {})}")
        if data['items']:
            print(f"   Первая запись: доход = {data['items'][0]['revenue']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 7. Комбинированная фильтрация
    print("\n7. Комбинированная фильтрация (year=2023&revenue_min=1000000):")
    response = requests.get(f"{base_url}/api/financial-indicators?year=2023&revenue_min=1000000")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Найдено записей: {data['total']}")
        print(f"   Примененные фильтры: {data.get('filters_applied', {})}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # 8. Пагинация
    print("\n8. Пагинация (page=1&per_page=1):")
    response = requests.get(f"{base_url}/api/organizations?page=1&per_page=1")
    if response.status_code == 200:
        data = response.json()
        print(f"   Статус: {response.status_code}")
        print(f"   Всего записей: {data['total']}")
        print(f"   Записей на странице: {len(data['items'])}")
        print(f"   Текущая страница: {data['current_page']}")
        print(f"   Всего страниц: {data['pages']}")
        print(f"   Есть следующая страница: {data['has_next']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

if __name__ == "__main__":
    test_api_filters()
