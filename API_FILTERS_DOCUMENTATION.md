# Документация по фильтрации API

## Обзор

API поддерживает мощную систему фильтрации данных с различными типами фильтров для всех эндпоинтов.

## Поддерживаемые эндпоинты с фильтрацией

- `/api/organizations` - Организации
- `/api/financial-indicators` - Финансовые показатели
- `/api/taxes` - Налоговые данные
- `/api/contacts` - Контакты
- `/api/addresses` - Адреса
- `/api/okveds` - ОКВЭД коды

## Типы фильтрации

### 1. Точное значение
Фильтрация по точному совпадению значения поля.

**Синтаксис:** `?field=value`

**Примеры:**
```bash
# Найти организацию по ИНН
GET /api/organizations?inn=1234567890

# Найти финансовые показатели за 2023 год
GET /api/financial-indicators?year=2023

# Найти контакты определенного типа
GET /api/contacts?contact_type=Основной
```

### 2. Диапазон значений (для числовых полей)
Фильтрация по минимальному и/или максимальному значению.

**Синтаксис:** 
- `?field_min=value` - минимальное значение
- `?field_max=value` - максимальное значение
- `?field_min=value&field_max=value` - диапазон

**Примеры:**
```bash
# Финансовые показатели с доходом от 500,000
GET /api/financial-indicators?revenue_min=500000

# Финансовые показатели с доходом от 100,000 до 1,000,000
GET /api/financial-indicators?revenue_min=100000&revenue_max=1000000

# Налоги за период с 2020 по 2023 год
GET /api/taxes?year_min=2020&year_max=2023
```

### 3. Поиск по подстроке (для строковых полей)
Поиск записей, содержащих указанную подстроку в поле.

**Синтаксис:** `?field_like=substring`

**Примеры:**
```bash
# Найти организации, содержащие "Тест" в названии
GET /api/organizations?name_like=Тест

# Найти контакты с email, содержащим "test"
GET /api/contacts?email_like=test

# Найти адреса в определенном районе
GET /api/addresses?district_like=Центральный
```

### 4. Общий поиск
Поиск по всем текстовым полям модели одновременно.

**Синтаксис:** `?search=text`

**Примеры:**
```bash
# Поиск по всем текстовым полям организаций
GET /api/organizations?search=организация

# Поиск по всем полям финансовых показателей
GET /api/financial-indicators?search=2023
```

## Сортировка

### Параметры сортировки
- `sort_by=field` - поле для сортировки
- `sort_order=asc|desc` - порядок сортировки (по умолчанию: asc)

**Примеры:**
```bash
# Сортировка по названию организации (по возрастанию)
GET /api/organizations?sort_by=name&sort_order=asc

# Сортировка по доходу (по убыванию)
GET /api/financial-indicators?sort_by=revenue&sort_order=desc

# Сортировка по году (по возрастанию)
GET /api/taxes?sort_by=year
```

## Пагинация

### Параметры пагинации
- `page=number` - номер страницы (по умолчанию: 1)
- `per_page=number` - количество записей на странице (по умолчанию: 50, максимум: 1000)

**Примеры:**
```bash
# Первая страница с 10 записями
GET /api/organizations?page=1&per_page=10

# Вторая страница
GET /api/organizations?page=2&per_page=50
```

## Комбинирование фильтров

Все типы фильтров можно комбинировать в одном запросе.

**Примеры:**
```bash
# Организации с доходом от 500,000 за 2023 год, отсортированные по убыванию дохода
GET /api/financial-indicators?revenue_min=500000&year=2023&sort_by=revenue&sort_order=desc

# Контакты типа "Основной" с email, содержащим "test", на первой странице
GET /api/contacts?contact_type=Основной&email_like=test&page=1&per_page=10

# Адреса в Центральном районе, отсортированные по полному адресу
GET /api/addresses?district_like=Центральный&sort_by=full_address
```

## Формат ответа

Все запросы возвращают данные в следующем формате:

```json
{
  "items": [...],                    // Массив записей
  "total": 100,                     // Общее количество записей
  "pages": 5,                       // Общее количество страниц
  "current_page": 1,                // Текущая страница
  "per_page": 50,                   // Записей на странице
  "has_next": true,                 // Есть ли следующая страница
  "has_prev": false,                // Есть ли предыдущая страница
  "filters_applied": {              // Примененные фильтры
    "field": "value",
    "field_like": "substring"
  }
}
```

## Примеры использования

### Поиск организаций
```bash
# Все организации
GET /api/organizations

# Организации с названием, содержащим "ООО"
GET /api/organizations?name_like=ООО

# Организации с определенным статусом
GET /api/organizations?final_status=Действующая

# Поиск по всем полям
GET /api/organizations?search=Москва
```

### Анализ финансовых показателей
```bash
# Показатели за 2023 год
GET /api/financial-indicators?year=2023

# Организации с доходом более 1 млн
GET /api/financial-indicators?revenue_min=1000000

# Топ-10 по доходу
GET /api/financial-indicators?sort_by=revenue&sort_order=desc&per_page=10

# Организации с количеством сотрудников от 10 до 100
GET /api/financial-indicators?employee_count_min=10&employee_count_max=100
```

### Анализ налоговых данных
```bash
# Налоги за 2023 год
GET /api/taxes?year=2023

# Организации с налогами в Москве более 50,000
GET /api/taxes?moscow_taxes_min=50000

# Сортировка по общему объему налогов
GET /api/taxes?sort_by=moscow_taxes&sort_order=desc
```

### Работа с контактами
```bash
# Все контакты
GET /api/contacts

# Основные контакты
GET /api/contacts?contact_type=Основной

# Контакты с определенным email
GET /api/contacts?email_like=@company.ru
```

### Географический анализ
```bash
# Все адреса
GET /api/addresses

# Адреса в определенном районе
GET /api/addresses?district=Центральный

# Адреса с координатами
GET /api/addresses?latitude_min=55.7&latitude_max=55.8
```

## Обработка ошибок

При ошибках API возвращает JSON с описанием ошибки:

```json
{
  "error": "Описание ошибки"
}
```

**Коды ошибок:**
- `400` - Неверные параметры запроса
- `500` - Внутренняя ошибка сервера

## Производительность

- Максимальное количество записей на странице: 1000
- Рекомендуемый размер страницы: 50-100 записей
- Индексы в базе данных оптимизированы для часто используемых полей фильтрации

## Ограничения

- Фильтрация по датам поддерживается только для строковых полей
- Поиск по подстроке не чувствителен к регистру
- Общий поиск работает только по текстовым полям
- Максимальная длина поискового запроса: 255 символов
