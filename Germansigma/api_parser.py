from __future__ import annotations
from typing import Any, Dict, Optional, List, Union
import requests

Json = Union[Dict[str, Any], List[Any]]

def _to_null(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.lower() in {"nan", "none", "null", "н/д", "нет данных", "—", "-"}:
            return None
        return s
    return v

def _pick(obj: Dict[str, Any], key: str) -> Any:
    """Безопасно достаёт значение по ключу из словаря API (или None, если ключа нет)."""
    return _to_null(obj.get(key))

def _collect_year_data_flat(obj: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
    """
    Собирает пары {год: значение} из ПЛОСКОГО словаря по ключам, где
    есть подстрока keyword и в конце стоит год (4 цифры).
    """
    result: Dict[str, Any] = {}
    for k, v in obj.items():
        try:
            k_str = str(k).strip()
        except Exception:
            continue
        if keyword in k_str:
            parts = k_str.split()
            year = parts[-1]
            if year.isdigit() and len(year) > 1:
                result[year] = _to_null(v)
    return result or None

def _collect_year_data_nested(obj: Any, keyword: str) -> Optional[Dict[str, Any]]:
    """
    Более общий вариант: ищет вложенный объект вида
    { "2019": ..., "2020": ..., ... } под ключом, содержащим keyword.
    Если находит — возвращает как есть (с приведением значений).
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and keyword in k:
                # если v уже dict с годами
                if isinstance(v, dict):
                    out: Dict[str, Any] = {}
                    for yk, yv in v.items():
                        if isinstance(yk, str) and yk.isdigit() and len(yk) == 4:
                            out[yk] = _to_null(yv)
                    return out or None
            # рекурсивный поиск
            nested = _collect_year_data_nested(v, keyword)
            if nested:
                return nested
    elif isinstance(obj, list):
        for it in obj:
            nested = _collect_year_data_nested(it, keyword)
            if nested:
                return nested
    return None

def _collect_year_data(obj: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
    """
    Сначала пробуем найти вложенный блок с годами (nested),
    иначе собираем из плоских ключей (flat).
    """
    nested = _collect_year_data_nested(obj, keyword)
    if nested:
        return nested
    return _collect_year_data_flat(obj, keyword)

def build_company_from_api(api_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Преобразует объект компании из API (dict) в целевой JSON.
    Ожидается, что ключи в API уже русскоязычные (как в Excel-версии).
    Если в API другой нейминг — добавь словарь соответствий (alias_map).
    """
    data: Dict[str, Any] = {
        "№": _pick(api_obj, "№"),
        "ИНН": _pick(api_obj, "ИНН"),
        "Наименование организации": _pick(api_obj, "Наименование организации"),
        "Полное наименование организации": _pick(api_obj, "Полное наименование организации"),
        "Статус СПАРК": _pick(api_obj, "Статус СПАРК"),
        "Статус внутренний": _pick(api_obj, "Статус внутренний"),
        "Статус ИТОГ": _pick(api_obj, "Статус ИТОГ"),
        "Дата добавления в реестр": _pick(api_obj, "Дата добавления в реестр"),
        "Юридический адрес": _pick(api_obj, "Юридический адрес"),
        "Адрес производства": _pick(api_obj, "Адрес производства"),
        "Адрес дополнительной площадки": _pick(api_obj, "Адрес дополнительной площадки"),
        "Основная отрасль": _pick(api_obj, "Основная отрасль"),
        "Подотрасль (Основная)": _pick(api_obj, "Подотрасль (Основная)"),
        "Дополнительная отрасль": _pick(api_obj, "Дополнительная отрасль"),
        "Подотрасль (Дополнительная)": _pick(api_obj, "Подотрасль (Дополнительная)"),
        "Основной ОКВЭД (СПАРК)": _pick(api_obj, "Основной ОКВЭД (СПАРК)"),
        "Вид деятельности по основному ОКВЭД (СПАРК)": _pick(api_obj, "Вид деятельности по основному ОКВЭД (СПАРК)"),
        "Производственный ОКВЭД": _pick(api_obj, "Производственный ОКВЭД"),
        "Вид деятельности по производственному ОКВЭД": _pick(api_obj, "Вид деятельности по производственному ОКВЭД"),
        "Общие сведения об организации": _pick(api_obj, "Общие сведения об организации"),
        "Размер предприятия (итог)": _pick(api_obj, "Размер предприятия (итог)"),
        "Размер предприятия (по численности)": _pick(api_obj, "Размер предприятия (по численности)"),
        "Размер предприятия (по выручке)": _pick(api_obj, "Размер предприятия (по выручке)"),
        "Дата регистрации": _pick(api_obj, "Дата регистрации"),
        "Руководитель": _pick(api_obj, "Руководитель"),
        "Контактные данные руководства": _pick(api_obj, "Контактные данные руководства"),
        "Почта руководства": _pick(api_obj, "Почта руководства"),
        "Контакт сотрудника организации": _pick(api_obj, "Контакт сотрудника организации"),
        "Номер телефона": _pick(api_obj, "Номер телефона"),
        "Сайт": _pick(api_obj, "Сайт"),
        "Электронная почта": _pick(api_obj, "Электронная почта"),
        "Системообразующее предприятие": _pick(api_obj, "Системообразующее предприятие"),
        "Статус МСП": _pick(api_obj, "Статус МСП"),
        "Площадка итог": _pick(api_obj, "Площадка итог"),
    }

    # Финансово-экономические показатели (автосбор по годам)
    data["Финансово-экономические показатели"] = {
        "Выручка предприятия, тыс. руб.": _collect_year_data(api_obj, "Выручка предприятия, тыс. руб."),
        "Чистая прибыль (убыток), тыс. руб.": _collect_year_data(api_obj, "Чистая прибыль (убыток)"),
        "Среднесписочная численность персонала (всего по компании), чел": _collect_year_data(api_obj, "Среднесписочная численность персонала (всего по компании)"),
        "Фонд оплаты труда всех сотрудников организации, тыс. руб.": _collect_year_data(api_obj, "Фонд оплаты труда всех сотрудников организации"),
        "НДФЛ, тыс. руб.": _collect_year_data(api_obj, "НДФЛ, тыс.руб."),
        "Налог на прибыль, тыс. руб.": _collect_year_data(api_obj, "Налог на прибыль"),
    }

    # Имущественно-земельный комплекс
    imzk = api_obj.get("Имущественно-земельный комплекс", {})
    if isinstance(imzk, dict):
        data["Имущественно-земельный комплекс"] = {
            "Кадастровый номер ЗУ": _pick(imzk, "Кадастровый номер ЗУ") or _pick(api_obj, "Кадастровый номер ЗУ"),
            "Площадь ЗУ (га)": _pick(imzk, "Площадь ЗУ (га)") or _pick(api_obj, "Площадь ЗУ"),
            "Вид разрешенного использования ЗУ": _pick(imzk, "Вид разрешенного использования ЗУ") or _pick(api_obj, "Вид разрешенного использования ЗУ"),
            "Вид собственности ЗУ": _pick(imzk, "Вид собственности ЗУ") or _pick(api_obj, "Вид собственности ЗУ"),
            "Кадастровый номер ОКСа": _pick(imzk, "Кадастровый номер ОКСа") or _pick(api_obj, "Кадастровый номер ОКСа"),
            "Площадь ОКСов (кв.м)": _pick(imzk, "Площадь ОКСов (кв.м)") or _pick(api_obj, "Площадь ОКСов"),
            "Вид собственности ОКСов": _pick(imzk, "Вид собственности ОКСов") or _pick(api_obj, "Вид собственности ОКСов"),
        }
    else:
        data["Имущественно-земельный комплекс"] = {
            "Кадастровый номер ЗУ": _pick(api_obj, "Кадастровый номер ЗУ"),
            "Площадь ЗУ (га)": _pick(api_obj, "Площадь ЗУ"),
            "Вид разрешенного использования ЗУ": _pick(api_obj, "Вид разрешенного использования ЗУ"),
            "Вид собственности ЗУ": _pick(api_obj, "Вид собственности ЗУ"),
            "Кадастровый номер ОКСа": _pick(api_obj, "Кадастровый номер ОКСа"),
            "Площадь ОКСов (кв.м)": _pick(api_obj, "Площадь ОКСов"),
            "Вид собственности ОКСов": _pick(api_obj, "Вид собственности ОКСов"),
        }

    # Производимая продукция
    prod = api_obj.get("Производимая продукция", {})
    if not isinstance(prod, dict):
        prod = {}
    codes_raw = prod.get("Коды ОКПД 2") or _pick(api_obj, "Перечень производимой продукции по кодам ОКПД 2")
    if isinstance(codes_raw, str):
        codes = [c.strip() for c in codes_raw.replace(",", ";").split(";") if c.strip()]
    elif isinstance(codes_raw, list):
        codes = [_to_null(c) for c in codes_raw]
    else:
        codes = None

    countries_raw = prod.get("Перечень государств") or _pick(api_obj, "Перечень государств куда экспортируется продукция")
    if isinstance(countries_raw, str):
        countries = [s.strip() for s in countries_raw.replace(",", ";").split(";") if s.strip()]
    elif isinstance(countries_raw, list):
        countries = [_to_null(s) for s in countries_raw]
    else:
        countries = None

    data["Производимая продукция"] = {
        "Название": prod.get("Название") or _pick(api_obj, "Название (виды производимой продукции)"),
        "Коды ОКПД 2": codes,
        "Наличие госзаказа": prod.get("Наличие госзаказа") or _pick(api_obj, "Наличие госзаказа"),
        "Наличие поставок продукции на экспорт": prod.get("Наличие поставок продукции на экспорт") or _pick(api_obj, "Наличие поставок продукции на экспорт"),
        "Объем экспорта (млн руб.)": prod.get("Объем экспорта (млн руб.)") or _pick(api_obj, "Объем экспорта (млн.руб.) за предыдущий календарный год"),
        "Перечень государств": countries,
    }

    # Координаты
    coords = api_obj.get("Координаты", {})
    if not isinstance(coords, dict):
        coords = {}
    data["Координаты"] = {
        "Широта": coords.get("Широта") or _pick(api_obj, "Координаты (широта)"),
        "Долгота": coords.get("Долгота") or _pick(api_obj, "Координаты (долгота)"),
        "Округ": coords.get("Округ") or _pick(api_obj, "Округ"),
        "Район": coords.get("Район") or _pick(api_obj, "Район"),
    }

    return data

# загрузка из API

def fetch_and_parse_company(
    url: Optional[str] = None,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    api_json: Optional[Json] = None,
) -> Dict[str, Any]:
    """
    Либо передай готовый JSON в api_json, либо укажи url (тогда функция сама сходить в API).
    Возвращает объект компании в целевой структуре.
    Если API возвращает массив компаний — берётся первая.
    """
    if api_json is None:
        if not url:
            raise ValueError("Нужно передать либо api_json, либо url")
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        api_json = resp.json()

    # Если это массив — возьмём первый элемент
    if isinstance(api_json, list):
        if not api_json:
            return build_company_from_api({})
        obj = api_json[0] if isinstance(api_json[0], dict) else {}
        return build_company_from_api(obj)

    # Если это объект — сразу парсим
    if isinstance(api_json, dict):
        return build_company_from_api(api_json)

    # Неизвестный формат
    return build_company_from_api({})


print(fetch_and_parse_company("http://localhost/"))
