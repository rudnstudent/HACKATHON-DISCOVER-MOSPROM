#!/usr/bin/env python3
"""
Скрипт для генерации случайных данных в базу данных
"""

import os
import random
from datetime import datetime, timedelta
from faker import Faker
import sqlalchemy
from data import db_session
from data.organization import Organization
from data.FinancialIndicator import FinancialIndicator
from data.Tax import Tax
from data.Contact import Contact
from data.adresses import Address
from data.Okved import Okved
from data.Industry import Industry
from data.CompanySize import CompanySize
from data.Support import Support
from data.InvestmentExport import InvestmentExport
from data.PropertyLand import PropertyLand
from data.Production import Production

# Настройка Faker для русского языка
fake = Faker('ru_RU')

# Конфигурация генерации
CONFIG = {
    'organizations_count': 1000,
    'years_range': [2020, 2021, 2022, 2023, 2024],
    'revenue_range': (100000, 10000000),  # тыс. руб
    'employee_range': (5, 500),
    'moscow_districts': [
        'Центральный', 'Северный', 'Северо-Восточный', 'Восточный',
        'Юго-Восточный', 'Южный', 'Юго-Западный', 'Западный',
        'Северо-Западный', 'Зеленоградский', 'Новомосковский', 'Троицкий'
    ],
    'industries': [
        'Производство', 'IT и телекоммуникации', 'Строительство',
        'Торговля', 'Транспорт и логистика', 'Финансы и страхование',
        'Образование', 'Здравоохранение', 'Энергетика',
        'Машиностроение', 'Химическая промышленность', 'Пищевая промышленность'
    ],
    'company_sizes': ['Микропредприятие', 'Малое предприятие', 'Среднее предприятие', 'Крупное предприятие'],
    'okved_codes': [
        '46.11', '46.12', '46.13', '46.14', '46.15',  # Торговля
        '62.01', '62.02', '62.03', '62.09',  # IT
        '41.10', '41.20', '42.11', '42.12',  # Строительство
        '10.11', '10.12', '10.13', '10.14',  # Пищевая промышленность
        '28.11', '28.12', '28.13', '28.14',  # Машиностроение
        '20.11', '20.12', '20.13', '20.14',  # Химическая промышленность
    ]
}

def generate_inn():
    """Генерирует случайный ИНН"""
    return str(random.randint(1000000000, 9999999999))

def generate_phone():
    """Генерирует случайный телефон"""
    return f"+7{random.randint(9000000000, 9999999999)}"

def generate_email(company_name):
    """Генерирует email на основе названия компании"""
    domain = company_name.lower().replace(' ', '').replace('"', '').replace('ооо', '').replace('оао', '')
    if len(domain) < 3:
        domain = fake.word()
    return f"info@{domain}.ru"

def generate_website(company_name):
    """Генерирует веб-сайт на основе названия компании"""
    domain = company_name.lower().replace(' ', '').replace('"', '').replace('ооо', '').replace('оао', '')
    if len(domain) < 3:
        domain = fake.word()
    return f"https://{domain}.ru"

def generate_organization():
    """Генерирует случайную организацию"""
    company_type = random.choice(['ООО', 'ОАО', 'ЗАО', 'ПАО', 'ИП'])
    company_name = fake.company()
    
    return Organization(
        inn=generate_inn(),
        name=f"{company_type} \"{company_name}\"",
        full_name=f"{company_type} \"{company_name}\"",
        spark_status=random.choice(['Активная', 'Неактивная', 'В процессе ликвидации']),
        internal_status=random.choice(['Работает', 'Приостановлена', 'Ликвидируется']),
        final_status=random.choice(['Действующая', 'Ликвидированная', 'Недействующая']),
        registry_addition_date=fake.date_between(start_date='-5y', end_date='today').strftime('%Y-%m-%d'),
        registration_date=fake.date_between(start_date='-10y', end_date='-1y').strftime('%Y-%m-%d'),
        manager_name=fake.name(),
        website=generate_website(company_name),
        email=generate_email(company_name),
        general_info=fake.text(max_nb_chars=500),
        head_organization=fake.company() if random.random() < 0.3 else None,
        head_organization_inn=generate_inn() if random.random() < 0.3 else None,
        head_organization_relation_type=random.choice(['Дочерняя', 'Филиал', 'Представительство']) if random.random() < 0.3 else None
    )

def generate_financial_indicator(organization_id):
    """Генерирует финансовые показатели для организации"""
    year = random.choice(CONFIG['years_range'])
    revenue = random.uniform(*CONFIG['revenue_range'])
    employee_count = random.randint(*CONFIG['employee_range'])
    moscow_ratio = random.uniform(0.3, 0.9)  # Доля московских сотрудников
    
    return FinancialIndicator(
        organization_id=organization_id,
        year=year,
        revenue=round(revenue, 2),
        net_profit=round(revenue * random.uniform(-0.1, 0.3), 2),
        employee_count=employee_count,
        employee_count_moscow=int(employee_count * moscow_ratio),
        payroll_all_employees=round(revenue * random.uniform(0.2, 0.6), 2),
        payroll_moscow_employees=round(revenue * random.uniform(0.1, 0.4), 2),
        avg_salary_all_employees=round(revenue * random.uniform(0.2, 0.6) / employee_count, 2),
        avg_salary_moscow_employees=round(revenue * random.uniform(0.1, 0.4) / int(employee_count * moscow_ratio), 2)
    )

def generate_tax(organization_id):
    """Генерирует налоговые данные для организации"""
    year = random.choice(CONFIG['years_range'])
    moscow_taxes = random.uniform(10000, 500000)
    
    return Tax(
        organization_id=organization_id,
        year=year,
        moscow_taxes=round(moscow_taxes, 2),
        profit_tax=round(moscow_taxes * random.uniform(0.2, 0.4), 2),
        property_tax=round(moscow_taxes * random.uniform(0.1, 0.2), 2),
        land_tax=round(moscow_taxes * random.uniform(0.05, 0.15), 2),
        personal_income_tax=round(moscow_taxes * random.uniform(0.3, 0.5), 2),
        transport_tax=round(moscow_taxes * random.uniform(0.01, 0.05), 2),
        other_taxes=round(moscow_taxes * random.uniform(0.05, 0.15), 2),
        excise_taxes=round(moscow_taxes * random.uniform(0, 0.1), 2)
    )

def generate_contact(organization_id):
    """Генерирует контактную информацию для организации"""
    return Contact(
        organization_id=organization_id,
        contact_type=random.choice(['Основной', 'Дополнительный', 'Технический', 'Коммерческий']),
        name=fake.name(),
        phone=generate_phone(),
        email=fake.email(),
        management_email=fake.email()
    )

def generate_address(organization_id):
    """Генерирует адресную информацию для организации"""
    district = random.choice(CONFIG['moscow_districts'])
    
    return Address(
        organization_id=organization_id,
        address_type=random.choice(['Юридический', 'Фактический', 'Почтовый']),
        full_address=f"г. Москва, {district} район, {fake.street_address()}",
        latitude=round(55.5 + random.uniform(-0.3, 0.3), 6),
        longitude=round(37.3 + random.uniform(-0.5, 0.5), 6),
        district=district,
        area=fake.city_suffix()
    )

def generate_okved(organization_id):
    """Генерирует ОКВЭД коды для организации"""
    code = random.choice(CONFIG['okved_codes'])
    
    return Okved(
        organization_id=organization_id,
        okved_type=random.choice(['Основной', 'Дополнительный']),
        code=code,
        description=fake.sentence(nb_words=6)
    )

def generate_industry(organization_id):
    """Генерирует отраслевую информацию для организации"""
    main_industry = random.choice(CONFIG['industries'])
    
    return Industry(
        organization_id=organization_id,
        main_industry=main_industry,
        main_subindustry=fake.word() + ' ' + main_industry.lower(),
        additional_industry=random.choice(CONFIG['industries']) if random.random() < 0.3 else None,
        additional_subindustry=fake.word() + ' ' + random.choice(CONFIG['industries']).lower() if random.random() < 0.3 else None,
        industry_presentations=fake.text(max_nb_chars=200),
        industry_by_spark=main_industry
    )

def generate_company_size(organization_id):
    """Генерирует размер компании для организации"""
    year = random.choice(CONFIG['years_range'])
    size = random.choice(CONFIG['company_sizes'])
    
    return CompanySize(
        organization_id=organization_id,
        year=year,
        size_final=size,
        size_by_employees=size,
        size_by_revenue=size
    )

def generate_support(organization_id):
    """Генерирует данные о поддержке для организации"""
    return Support(
        organization_id=organization_id,
        support_data=fake.text(max_nb_chars=100),
        special_status=random.choice(['Инновационная', 'Социально значимая', 'Экспортно-ориентированная', None]),
        platform_final=random.choice(['МСП', 'Крупный бизнес', 'Стартап']),
        moscow_support_received=random.choice([True, False]),
        system_forming_enterprise=random.choice([True, False]),
        sme_status=random.choice(['Микропредприятие', 'Малое предприятие', 'Среднее предприятие', 'Крупное предприятие'])
    )

def generate_investment_export(organization_id):
    """Генерирует данные об инвестициях и экспорте для организации"""
    year = random.choice(CONFIG['years_range'])
    
    return InvestmentExport(
        organization_id=organization_id,
        year=year,
        moscow_investments=round(random.uniform(100000, 5000000), 2),
        export_volume=round(random.uniform(0, 2000000), 2)
    )

def generate_property_land(organization_id):
    """Генерирует данные об имущественно-земельном комплексе для организации"""
    return PropertyLand(
        organization_id=organization_id,
        land_cadastral_number=f"77:{random.randint(10000000, 99999999)}:{random.randint(1000, 9999)}:{random.randint(100, 999)}",
        land_area=round(random.uniform(100, 10000), 2),
        land_use_type=random.choice(['Промышленное', 'Коммерческое', 'Складское', 'Производственное']),
        land_ownership_type=random.choice(['Собственность', 'Аренда', 'Безвозмездное пользование']),
        land_owner=fake.company(),
        building_cadastral_number=f"77:{random.randint(10000000, 99999999)}:{random.randint(1000, 9999)}:{random.randint(100, 999)}",
        building_area=round(random.uniform(500, 50000), 2),
        building_use_type=random.choice(['Производственное', 'Офисное', 'Складское', 'Административное']),
        building_type_purpose=random.choice(['Производство', 'Офисы', 'Склады', 'Лаборатории']),
        building_ownership_type=random.choice(['Собственность', 'Аренда', 'Оперативное управление']),
        building_owner=fake.company(),
        production_area=round(random.uniform(200, 20000), 2)
    )

def generate_production(organization_id):
    """Генерирует производственную информацию для организации"""
    year = random.choice(CONFIG['years_range'])
    
    return Production(
        organization_id=organization_id,
        year=year,
        manufactured_products=fake.text(max_nb_chars=200),
        standardized_products=fake.text(max_nb_chars=150),
        product_names=fake.text(max_nb_chars=100),
        okpd2_products=fake.text(max_nb_chars=100),
        product_types_segments=fake.text(max_nb_chars=150),
        product_catalog=fake.text(max_nb_chars=200),
        government_order=random.choice([True, False]),
        production_capacity_utilization=random.choice(['0-25%', '25-50%', '50-75%', '75-100%']),
        export_supplies=random.choice([True, False]),
        export_volume_previous_year=round(random.uniform(0, 1000000), 2),
        export_countries=fake.country() + ', ' + fake.country() if random.random() < 0.5 else fake.country(),
        tn_ved_code=f"{random.randint(10, 99)}.{random.randint(10, 99)}.{random.randint(10, 99)}.{random.randint(10, 99)}"
    )

def clear_database(session):
    """Очищает базу данных"""
    print("Очистка базы данных...")
    
    # Удаляем в правильном порядке (сначала зависимые таблицы)
    session.query(Production).delete()
    session.query(PropertyLand).delete()
    session.query(InvestmentExport).delete()
    session.query(Support).delete()
    session.query(CompanySize).delete()
    session.query(Industry).delete()
    session.query(Okved).delete()
    session.query(Address).delete()
    session.query(Contact).delete()
    session.query(Tax).delete()
    session.query(FinancialIndicator).delete()
    session.query(Organization).delete()
    
    session.commit()
    print("База данных очищена")

def generate_data():
    """Основная функция генерации данных"""
    # Инициализация базы данных
    db_path = os.path.join(os.path.dirname(__file__), "db/database_test.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)
    
    session = db_session.create_session()
    
    try:
        # Очищаем базу данных
        clear_database(session)
        
        print(f"Генерация {CONFIG['organizations_count']} организаций...")
        
        # Генерируем организации
        organizations = []
        for i in range(CONFIG['organizations_count']):
            if (i + 1) % 100 == 0:
                print(f"Создано организаций: {i + 1}")
            
            org = generate_organization()
            session.add(org)
            session.flush()  # Получаем ID
            organizations.append(org)
        
        session.commit()
        print(f"Создано {len(organizations)} организаций")
        
        # Генерируем связанные данные для каждой организации
        for i, org in enumerate(organizations):
            if (i + 1) % 100 == 0:
                print(f"Обработано организаций: {i + 1}")
            
            # Финансовые показатели (несколько лет)
            for year in random.sample(CONFIG['years_range'], random.randint(1, 3)):
                fin_ind = generate_financial_indicator(org.id)
                fin_ind.year = year
                session.add(fin_ind)
            
            # Налоговые данные
            tax = generate_tax(org.id)
            session.add(tax)
            
            # Контакты
            contact = generate_contact(org.id)
            session.add(contact)
            
            # Адреса
            address = generate_address(org.id)
            session.add(address)
            
            # ОКВЭД
            okved = generate_okved(org.id)
            session.add(okved)
            
            # Отрасли
            industry = generate_industry(org.id)
            session.add(industry)
            
            # Размеры компаний
            company_size = generate_company_size(org.id)
            session.add(company_size)
            
            # Поддержка
            support = generate_support(org.id)
            session.add(support)
            
            # Инвестиции и экспорт
            investment = generate_investment_export(org.id)
            session.add(investment)
            
            # Имущественно-земельный комплекс
            property_land = generate_property_land(org.id)
            session.add(property_land)
            
            # Производство
            production = generate_production(org.id)
            session.add(production)
        
        session.commit()
        print("Все данные успешно сгенерированы!")
        
        # Выводим статистику
        print("\nСтатистика:")
        print(f"Организаций: {session.query(Organization).count()}")
        print(f"Финансовых показателей: {session.query(FinancialIndicator).count()}")
        print(f"Налоговых данных: {session.query(Tax).count()}")
        print(f"Контактов: {session.query(Contact).count()}")
        print(f"Адресов: {session.query(Address).count()}")
        print(f"ОКВЭД: {session.query(Okved).count()}")
        print(f"Отраслей: {session.query(Industry).count()}")
        print(f"Размеров компаний: {session.query(CompanySize).count()}")
        print(f"Поддержки: {session.query(Support).count()}")
        print(f"Инвестиций и экспорта: {session.query(InvestmentExport).count()}")
        print(f"Имущественно-земельного комплекса: {session.query(PropertyLand).count()}")
        print(f"Производства: {session.query(Production).count()}")
        
    except Exception as e:
        print(f"Ошибка при генерации данных: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Запуск генерации случайных данных...")
    print("Это может занять несколько минут...")
    
    try:
        generate_data()
        print("\nГенерация данных завершена успешно!")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
