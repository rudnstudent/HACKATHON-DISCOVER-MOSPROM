#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel -> API (POST). Поддерживаются эндпоинты:
organizations, financial-indicators, property-land, addresses, production,
investment-export, support, company-sizes, industries, okveds, taxes, contacts
"""
import sys, re, json, math
import pandas as pd
import requests
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, List

# ========= НАСТРОЙКИ =========
API_BASE = "http://localhost:5000/api"
TIMEOUT = 30
VERIFY_SSL = False

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})
session.verify = VERIFY_SSL

# ========= ХЕЛПЕРЫ ТИПОВ =========
def to_null(v: Any) -> Any:
    if v is None:
        return None
    try:
        if pd.isna(v): return None
    except Exception:
        pass
    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.lower() in {"nan","none","null","н/д","нет данных","—","-"}:
            return None
        return s
    return v

def to_bool(v: Any) -> Optional[bool]:
    v = to_null(v)
    if v is None: return None
    if isinstance(v, bool): return v
    s = str(v).strip().lower()
    t = {"true","1","yes","y","да","истина","верно","есть","ok","ок"}
    f = {"false","0","no","n","нет","ложь","неверно"}
    if s in t: return True
    if s in f: return False
    return None

_num_clean_re = re.compile(r"[^\d\.\,\-]+")

def to_float(v: Any) -> Optional[float]:
    v = to_null(v)
    if v is None: return None
    if isinstance(v, (int,float)) and not isinstance(v, bool):
        return float(v)
    s = str(v)
    s = _num_clean_re.sub("", s).replace(" ", "").replace("\u00A0","").replace(",", ".")
    try:
        if s in {"", ".", "-", "-.", ".-"}: return None
        return float(s)
    except Exception:
        return None

def to_int(v: Any) -> Optional[int]:
    f = to_float(v)
    if f is None or (isinstance(f,float) and math.isnan(f)): return None
    try:
        return int(round(f))
    except Exception:
        return None

def normalize_inn(v: Any) -> Optional[str]:
    s = to_null(v)
    if s is None: return None
    digits = re.sub(r"\D+", "", str(s))
    return digits[:12] if digits else None

def pick(row: pd.Series, *cols: str) -> Any:
    """Возвращает первое непустое значение из набора альтернативных колонок."""
    for col in cols:
        if col in row.index:
            val = to_null(row[col])
            if val is not None:
                return val
    return None

def collect_year_data(row: pd.Series, keyword: str) -> Dict[str, Any]:
    """Ищет колонки с ключевым словом и годом в конце."""
    result = {}
    for col in row.index:
        if keyword in col:
            parts = col.strip().split()
            year = parts[-1]
            if year.isdigit() and len(year) > 1:
                result[year] = to_null(row[col])
    return result or None

# ========= PAYLOAD BUILDERS (точно под columns_metadata) =========
def build_organization_payload(row: pd.Series) -> Dict[str, Any]:
    return {
        "inn": normalize_inn(pick(row, "ИНН")),
        "name": pick(row, "Наименование организации"),
        "full_name": pick(row, "Полное наименование организации"),
        "spark_status": pick(row, "Статус СПАРК"),
        "internal_status": pick(row, "Статус внутренний"),
        "final_status": pick(row, "Статус ИТОГ"),
        "registry_addition_date": pick(row, "Дата добавления в реестр"),
        "registration_date": pick(row, "Дата регистрации"),
        "manager_name": pick(row, "Руководитель"),
        "website": pick(row, "Сайт"),
        "email": pick(row, "Электронная почта"),
        "general_info": pick(row, "Общие сведения об организации"),
        "head_organization": pick(row, "Головная организация", "Головная организация (если есть)"),
        "head_organization_inn": normalize_inn(pick(row, "ИНН головной организации")),
        "head_organization_relation_type": pick(row, "Тип связи с головной"),
    }

def build_financial_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    revenue = collect_year_data(row, "Выручка предприятия")
    profit = collect_year_data(row, "Чистая прибыль")
    emp_total = collect_year_data(row, "Среднесписочная численность персонала (всего по компании)")
    payroll_total = collect_year_data(row, "Фонд оплаты труда всех сотрудников организации")
    # Доп. поля оставляем None, т.к. их нет в Excel
    years = set()
    for d in (revenue, profit, emp_total, payroll_total):
        if d: years.update(d.keys())
    out = []
    for y in sorted(years):
        out.append({
            "organization_id": organization_id,
            "year": int(y),
            "revenue": to_float(revenue.get(y)) if revenue else None,
            "net_profit": to_float(profit.get(y)) if profit else None,
            "employee_count": to_int(emp_total.get(y)) if emp_total else None,
            "employee_count_moscow": None,
            "payroll_all_employees": to_float(payroll_total.get(y)) if payroll_total else None,
            "payroll_moscow_employees": None,
            "avg_salary_all_employees": None,
            "avg_salary_moscow_employees": None,
        })
    return out

def build_property_land_payload(row: pd.Series, organization_id: int) -> Dict[str, Any]:
    return {
        "organization_id": organization_id,
        "land_cadastral_number": pick(row, "Кадастровый номер ЗУ"),
        "land_area": to_float(pick(row, "Площадь ЗУ", "Площадь ЗУ (га)")),
        "land_use_type": pick(row, "Вид разрешенного использования ЗУ"),
        "land_ownership_type": pick(row, "Вид собственности ЗУ"),
        "land_owner": pick(row, "Собственник ЗУ"),
        "building_cadastral_number": pick(row, "Кадастровый номер ОКСа"),
        "building_area": to_float(pick(row, "Площадь ОКСов", "Площадь ОКСов (кв.м)")),
        "building_use_type": pick(row, "Вид использования ОКСов"),
        "building_type_purpose": pick(row, "Тип/назначение ОКСов"),
        "building_ownership_type": pick(row, "Вид собственности ОКСов"),
        "building_owner": pick(row, "Собственник ОКСов"),
        "production_area": to_float(pick(row, "Производственная площадь")),
    }

def build_address_payload(row: pd.Series, organization_id: int) -> Dict[str, Any]:
    return {
        "organization_id": organization_id,
        "address_type": None,  # можно задать "legal"/"production" при наличии
        "full_address": pick(row, "Юридический адрес", "Адрес производства", "Адрес дополнительной площадки"),
        "latitude": to_float(pick(row, "Координаты (широта)")),
        "longitude": to_float(pick(row, "Координаты (долгота)")),
        "district": pick(row, "Округ"),
        "area": pick(row, "Район"),
    }

def infer_year_for_production(row: pd.Series) -> int:
    revenue = collect_year_data(row, "Выручка предприятия")
    years = [int(y) for y in (revenue or {}).keys() if y.isdigit()]
    return max(years) if years else datetime.now().year

def build_production_payload(row: pd.Series, organization_id: int) -> Dict[str, Any]:
    codes_raw = pick(row, "Перечень производимой продукции по кодам ОКПД 2")
    okpd2_flat = None
    if isinstance(codes_raw, str):
        parts = [c.strip() for c in codes_raw.replace(",", ";").split(";") if c.strip()]
        okpd2_flat = "; ".join(parts) if parts else None
    return {
        "year": infer_year_for_production(row),
        "organization_id": organization_id,
        "manufactured_products": pick(row, "Производимая продукция"),
        "standardized_products": pick(row, "Стандартизированная продукция"),
        "product_names": pick(row, "Название (виды производимой продукции)"),
        "okpd2_products": okpd2_flat,
        "product_types_segments": pick(row, "Сегменты/типы продукции"),
        "product_catalog": pick(row, "Каталог продукции (URL)", "Каталог продукции"),
        "government_order": to_bool(pick(row, "Наличие госзаказа")),
        "production_capacity_utilization": pick(row, "Загрузка мощностей, %"),
        "export_supplies": to_bool(pick(row, "Наличие поставок продукции на экспорт")),
        "export_volume_previous_year": to_float(pick(row, "Объем экспорта (млн.руб.) за предыдущий календарный год")),
        "export_countries": (
            "; ".join([s.strip() for s in pick(row, "Перечень государств куда экспортируется продукция").split(";")])
            if isinstance(pick(row, "Перечень государств куда экспортируется продукция"), str) else None
        ),
        "tn_ved_code": pick(row, "Код ТН ВЭД"),
    }

def build_investment_export_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    invest = collect_year_data(row, "Объем инвестиций Москвы") or collect_year_data(row, "Инвестиции Москвы")
    export = collect_year_data(row, "Объем экспорта") or collect_year_data(row, "Экспорт, млн")
    years = set()
    for d in (invest, export):
        if d: years.update(d.keys())
    out = []
    for y in sorted(years):
        out.append({
            "organization_id": organization_id,
            "year": int(y),
            "moscow_investments": to_float(invest.get(y)) if invest else None,
            "export_volume": to_float(export.get(y)) if export else None,
        })
    return out

def build_support_payload(row: pd.Series, organization_id: int) -> Dict[str, Any]:
    return {
        "organization_id": organization_id,
        "support_data": pick(row, "Поддержка (описание)", "Поддержка/меры"),
        "special_status": pick(row, "Спецстатус", "Специальный статус"),
        "platform_final": pick(row, "Площадка итог"),
        "moscow_support_received": to_bool(pick(row, "Поддержка Москвы получена", "Получали поддержку от Москвы")),
        "system_forming_enterprise": to_bool(pick(row, "Системообразующее предприятие")),
        "sme_status": pick(row, "Статус МСП"),
    }

def build_company_sizes_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    size_final = collect_year_data(row, "Размер предприятия (итог)")
    size_by_employees = collect_year_data(row, "Размер предприятия (по численности)")
    size_by_revenue = collect_year_data(row, "Размер предприятия (по выручке)")
    years = set()
    for d in (size_final, size_by_employees, size_by_revenue):
        if d: years.update(d.keys())
    out = []
    if not years and pick(row, "Размер предприятия (итог)"):
        # безгодовой вариант — запишем один раз с текущим годом
        years = {str(datetime.now().year)}
    for y in sorted(years):
        out.append({
            "organization_id": organization_id,
            "year": int(y),
            "size_final": (size_final or {}).get(y) or pick(row, "Размер предприятия (итог)"),
            "size_by_employees": (size_by_employees or {}).get(y),
            "size_by_revenue": (size_by_revenue or {}).get(y),
        })
    return out

def build_industries_payload(row: pd.Series, organization_id: int) -> Dict[str, Any]:
    return {
        "organization_id": organization_id,
        "main_industry": pick(row, "Основная отрасль"),
        "main_subindustry": pick(row, "Подотрасль (Основная)"),
        "additional_industry": pick(row, "Дополнительная отрасль"),
        "additional_subindustry": pick(row, "Подотрасль (Дополнительная)"),
        "industry_presentations": pick(row, "Презентации отрасли", "Ссылки/презентации отрасли"),
        "industry_by_spark": pick(row, "Отрасль по СПАРК", "Основной ОКВЭД (СПАРК)"),
    }

def build_okveds_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    out = []
    # Основной ОКВЭД (СПАРК)
    main_code = pick(row, "Основной ОКВЭД (СПАРК)")
    main_desc = pick(row, "Вид деятельности по основному ОКВЭД (СПАРК)")
    if main_code or main_desc:
        out.append({
            "organization_id": organization_id,
            "okved_type": "main_spark",
            "code": main_code,
            "description": main_desc
        })
    # Производственный ОКВЭД
    prod_code = pick(row, "Производственный ОКВЭД")
    prod_desc = pick(row, "Вид деятельности по производственному ОКВЭД")
    if prod_code or prod_desc:
        out.append({
            "organization_id": organization_id,
            "okved_type": "production",
            "code": prod_code,
            "description": prod_desc
        })
    return out

def build_taxes_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    # Собираем все налоги по годам
    moscow_taxes = collect_year_data(row, "Налоги в бюджет Москвы")
    profit_tax = collect_year_data(row, "Налог на прибыль")
    property_tax = collect_year_data(row, "Налог на имущество")
    land_tax = collect_year_data(row, "Земельный налог")
    personal_income_tax = collect_year_data(row, "НДФЛ")
    transport_tax = collect_year_data(row, "Транспортный налог")
    other_taxes = collect_year_data(row, "Прочие налоги")
    excise_taxes = collect_year_data(row, "Акцизы")

    years = set()
    for d in (moscow_taxes, profit_tax, property_tax, land_tax, personal_income_tax, transport_tax, other_taxes, excise_taxes):
        if d: years.update(d.keys())

    out = []
    for y in sorted(years):
        out.append({
            "organization_id": organization_id,
            "year": int(y),
            "moscow_taxes": to_float((moscow_taxes or {}).get(y)),
            "profit_tax": to_float((profit_tax or {}).get(y)),
            "property_tax": to_float((property_tax or {}).get(y)),
            "land_tax": to_float((land_tax or {}).get(y)),
            "personal_income_tax": to_float((personal_income_tax or {}).get(y)),
            "transport_tax": to_float((transport_tax or {}).get(y)),
            "other_taxes": to_float((other_taxes or {}).get(y)),
            "excise_taxes": to_float((excise_taxes or {}).get(y)),
        })
    return out

def build_contacts_payloads(row: pd.Series, organization_id: int) -> List[Dict[str, Any]]:
    # Простой кейс: один контакт из доступных полей
    contact_name = pick(row, "Контакт сотрудника организации", "Контактное лицо", "Руководитель")
    phone = pick(row, "Номер телефона", "Телефон")
    email = pick(row, "Электронная почта", "Почта руководства", "Email")
    out = []
    if contact_name or phone or email:
        out.append({
            "organization_id": organization_id,
            "contact_type": pick(row, "Тип контакта") or "general",
            "name": contact_name,
            "phone": phone,
            "email": email,
            "management_email": pick(row, "Почта руководства"),
        })
    return out

# ========= HTTP =========
def post_json(path: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    resp = session.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), timeout=TIMEOUT)
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text}
    ok = resp.status_code in (200, 201)
    print(f"{'✅' if ok else '❌'} POST {url} -> {resp.status_code} | {('id='+str(body.get('item').get('id'))) if ok else body}")
    return resp.status_code, body

# ========= ЦЕПОЧКА ДЛЯ ОДНОЙ СТРОКИ =========
def upsert_row(row: pd.Series):
    # 1) organizations
    org = build_organization_payload(row)
    if not org["inn"] or not org["name"]:
        print("⛔ Пропуск: обязательные поля inn/name пусты")
        return
    st, body = post_json("/organizations", org)
    if st not in (200, 201):
        print("⛔ Не создана организация — остановка цепочки")
        return

    org_id = body["item"]["id"]

    # 2) financial-indicators (много)
    for fi in build_financial_payloads(row, org_id):
        post_json("/financial-indicators", fi)

    # 3) property-land (1)
    post_json("/property-land", build_property_land_payload(row, org_id))

    # 4) addresses (1)
    post_json("/addresses", build_address_payload(row, org_id))

    # 5) production (1)
    post_json("/production", build_production_payload(row, org_id))

    # 6) investment-export (много)
    for inv in build_investment_export_payloads(row, org_id):
        post_json("/investment-export", inv)

    # 7) support (1)
    post_json("/support", build_support_payload(row, org_id))

    # 8) company-sizes (много/или 1 без годовых полей)
    for cs in build_company_sizes_payloads(row, org_id):
        post_json("/company-sizes", cs)

    # 9) industries (1)
    post_json("/industries", build_industries_payload(row, org_id))

    # 10) okveds (0..2)
    for okv in build_okveds_payloads(row, org_id):
        post_json("/okveds", okv)

    # 11) taxes (много)
    for tx in build_taxes_payloads(row, org_id):
        post_json("/taxes", tx)

    # 12) contacts (0..1)
    for c in build_contacts_payloads(row, org_id):
        post_json("/contacts", c)

# ========= MAIN =========
def excel_to_api(excel_path: str):
    print(excel_path)
    try:
        df = pd.read_excel(excel_path, dtype=str)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return 0
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
    if df.empty:
        print("Файл пуст")
        return 0

    print(f"Начинаем обработку {len(df)} записей")

    processed_count = 0
    for i, row in df.iterrows():
        print(f"\n📄 Строка {i+1}/{len(df)}")
        try:
            upsert_row(row)
            processed_count += 1
        except Exception as e:
            print(f"Ошибка обработки строки {i+1}: {e}")
            continue
    
    print(f"Обработано записей: {processed_count}")
    return processed_count
