# 🏭 Moscow Industry Database

Комплексная система для работы с данными о промышленных предприятиях Москвы, включающая веб-интерфейс, REST API и инструменты для анализа данных.

## ✨ Основные возможности

- 📊 **Динамическая фильтрация** - мощные инструменты поиска и фильтрации данных
- 🔍 **Сравнение компаний** - детальное сравнение до 3 компаний с визуализацией
- 📈 **Интерактивные графики** - автоматическое создание графиков для числовых данных
- 📤 **Экспорт данных** - CSV, Excel, PDF и изображения графиков
- 🔄 **Загрузка Excel** - импорт данных из Excel файлов с валидацией
- 🛠️ **REST API** - полный набор API для программного доступа
- 📚 **Swagger документация** - интерактивная документация API

## 🚀 Быстрый старт

### Требования

- Python 3.8+
- SQLite3
- Современный веб-браузер

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/moscow-industry-database.git
cd moscow-industry-database
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Запустите приложение:**
```bash
python main.py
```

4. **Откройте в браузере:**
```
http://localhost:5000
```

## 📁 Структура проекта

```
moscow-industry-database/
├── 📁 data/                    # Модели базы данных
│   ├── organization.py         # Модель организаций
│   ├── financial_indicator.py  # Финансовые показатели
│   ├── tax.py                  # Налоговые данные
│   └── ...                     # Другие модели
├── 📁 templates/               # HTML шаблоны
│   ├── index.html              # Главная страница
│   ├── dynamic_filter.html     # Динамические фильтры
│   ├── company_comparison.html # Сравнение компаний
│   └── upload_excel.html       # Загрузка Excel
├── 📁 static/                  # Статические файлы
│   ├── css/style.css           # Стили
│   └── js/                     # JavaScript
├── 📁 db/                      # База данных
├── api_crud_filters.py         # CRUD API
├── excel_api.py               # Обработка Excel
├── main.py                    # Основное приложение
└── requirements.txt           # Зависимости
```

## 🗄️ База данных

Система работает с 12 основными таблицами:

| Таблица | Описание |
|---------|----------|
| `organizations` | Основная информация об организациях |
| `financial_indicators` | Финансовые показатели по годам |
| `taxes` | Налоговые данные |
| `contacts` | Контактная информация |
| `addresses` | Адресные данные |
| `okveds` | Коды ОКВЭД |
| `industries` | Отраслевая информация |
| `company_sizes` | Размеры предприятий |
| `support` | Поддержка и статусы |
| `investment_export` | Инвестиции и экспорт |
| `property_land` | Имущественно-земельный комплекс |
| `production` | Производственная информация |

## 🔧 API Документация

### Основные эндпоинты

#### Получение данных
```http
GET /api/tables/{table_name}/data
GET /api/tables/{table_name}/data/{id}
GET /api/tables/{table_name}/stats
```

#### Создание и обновление
```http
POST /api/tables/{table_name}/data
PUT /api/tables/{table_name}/data/{id}
DELETE /api/tables/{table_name}/data/{id}
```

#### Специальные эндпоинты
```http
GET /api/companies/search?q={query}     # Поиск компаний
POST /api/compare/companies             # Сравнение компаний
```

### Примеры использования

**Поиск компаний:**
```bash
curl "http://localhost:5000/api/companies/search?q=Газпром"
```

**Получение финансовых показателей:**
```bash
curl "http://localhost:5000/api/tables/financial-indicators/data?year=2023"
```

**Сравнение компаний:**
```bash
curl -X POST "http://localhost:5000/api/compare/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "company_ids": [1, 2, 3],
    "selected_fields": {
      "organizations": ["name", "inn"],
      "financial-indicators": ["revenue", "net_profit"]
    }
  }'
```

## 🎨 Веб-интерфейс

### Главная страница
- Обзор системы и статистика
- Быстрый доступ к основным функциям
- Информация о проекте

### Динамические фильтры
- Поиск по всем таблицам базы данных
- Гибкая настройка фильтров
- Экспорт результатов

### Сравнение компаний
- Выбор до 3 компаний для сравнения
- Настройка сравниваемых характеристик
- Автоматическое создание графиков
- Экспорт в различных форматах

### Загрузка Excel
- Простой интерфейс загрузки файлов
- Валидация данных
- Индикатор прогресса
- Детальный отчет о результатах

## 📊 Визуализация данных

Система автоматически создает интерактивные графики для числовых данных:

- **Столбчатые диаграммы** - для сравнения значений
- **Линейные графики** - для временных рядов
- **Экспорт графиков** - PNG, PDF, ZIP архивы

## 🔄 Загрузка данных

### Поддерживаемые форматы
- Excel (.xlsx, .xls)
- Максимальный размер: 16 МБ

### Процесс загрузки
1. Выберите файл на странице загрузки
2. Система валидирует формат и структуру
3. Данные импортируются в базу данных
4. Создается отчет о результатах

## 🛠️ Разработка

### Установка для разработки

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/moscow-industry-database.git
cd moscow-industry-database
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Запустите в режиме разработки:**
```bash
python main.py
```

### Генерация тестовых данных

```bash
python generate_random_data.py
```

### Структура API

API построен на Flask-RESTful с поддержкой:
- CRUD операций для всех таблиц
- Фильтрации и сортировки
- Пагинации результатов
- Валидации данных

## 📋 Требования

### Системные требования
- Python 3.8+
- SQLite3
- 512 МБ RAM (минимум)
- 1 ГБ свободного места

### Python зависимости
```
Flask==2.3.3
Flask-RESTful==0.3.10
SQLAlchemy==2.0.21
pandas==2.1.4
numpy==1.24.3
openpyxl==3.1.2
faker==19.6.2
flasgger==0.9.7.1
python-dotenv==1.0.0
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для получения дополнительной информации.

## 📞 Поддержка

Если у вас есть вопросы или предложения:

- 📧 Email: support@moscow-industry.ru
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/moscow-industry-database/issues)
- 📖 Документация: [Wiki](https://github.com/yourusername/moscow-industry-database/wiki)

## 🏆 Благодарности

- Команде разработки за создание системы
- Сообществу Flask за отличный фреймворк
- Разработчикам Chart.js за библиотеку визуализации

---

**Moscow Industry Database** - Ваш надежный инструмент для работы с данными промышленных предприятий Москвы! 🏭✨