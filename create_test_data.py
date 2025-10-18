#!/usr/bin/env python3
"""
Создание тестовых данных для API
"""

from data.db_session import global_init
from data.organization import Organization
from data.FinancialIndicator import FinancialIndicator
from data.Tax import Tax
from data.adresses import Address
from data.Contact import Contact
from datetime import datetime

def create_test_data():
    """Создает тестовые данные"""
    
    # Инициализация базы данных
    session = global_init('db/database_test.db')
    
    # Создаем тестовую организацию
    org = Organization(
        inn='1234567890',
        name='Тестовая организация',
        full_name='ООО "Тестовая организация"',
        spark_status='Активная',
        internal_status='Работает',
        final_status='Действующая',
        registry_addition_date='2024-01-15',
        registration_date='2020-05-10',
        manager_name='Иванов Иван Иванович',
        website='https://test-org.ru',
        email='info@test-org.ru',
        general_info='Тестовая организация для проверки API',
        head_organization='Головная организация',
        head_organization_inn='0987654321',
        head_organization_relation_type='Дочерняя'
    )
    
    session.add(org)
    session.commit()
    
    # Создаем финансовые показатели
    financial = FinancialIndicator(
        organization_id=org.id,
        year=2023,
        revenue=1000000.50,
        net_profit=150000.25,
        employee_count=50,
        employee_count_moscow=45,
        payroll_all_employees=5000000.00,
        payroll_moscow_employees=4500000.00,
        avg_salary_all_employees=100000.00,
        avg_salary_moscow_employees=100000.00
    )
    
    session.add(financial)
    
    # Создаем налоговые данные
    tax = Tax(
        organization_id=org.id,
        year=2023,
        moscow_taxes=50000.00,
        profit_tax=30000.00,
        property_tax=10000.00,
        land_tax=5000.00,
        personal_income_tax=40000.00,
        transport_tax=2000.00,
        other_taxes=3000.00,
        excise_taxes=0.00
    )
    
    session.add(tax)
    
    # Создаем адрес
    address = Address(
        organization_id=org.id,
        address_type='Юридический',
        full_address='г. Москва, ул. Тестовая, д. 1',
        latitude=55.7558,
        longitude=37.6176,
        district='Центральный',
        area='Тверской'
    )
    
    session.add(address)
    
    # Создаем контакт
    contact = Contact(
        organization_id=org.id,
        contact_type='Основной',
        name='Петров Петр Петрович',
        phone='+7 (495) 123-45-67',
        email='contact@test-org.ru',
        management_email='management@test-org.ru'
    )
    
    session.add(contact)
    
    session.commit()
    
    print("Тестовые данные созданы успешно!")
    print(f"Организация: {org.name} (ID: {org.id})")
    print(f"Финансовые показатели: {session.query(FinancialIndicator).count()} записей")
    print(f"Налоговые данные: {session.query(Tax).count()} записей")
    print(f"Адреса: {session.query(Address).count()} записей")
    print(f"Контакты: {session.query(Contact).count()} записей")

if __name__ == "__main__":
    create_test_data()
