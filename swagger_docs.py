from flasgger import swag_from

# Swagger документация для API endpoints

ORGANIZATIONS_GET_DOC = {
    "tags": ["Organizations"],
    "summary": "Получить список организаций",
    "description": "Возвращает список организаций с возможностью фильтрации, сортировки и пагинации",
    "parameters": [
        {
            "name": "inn",
            "in": "query",
            "type": "string",
            "description": "ИНН организации"
        },
        {
            "name": "name",
            "in": "query",
            "type": "string",
            "description": "Название организации"
        },
        {
            "name": "name_like",
            "in": "query",
            "type": "string",
            "description": "Поиск по названию организации (подстрока)"
        },
        {
            "name": "spark_status",
            "in": "query",
            "type": "string",
            "description": "Статус СПАРК"
        },
        {
            "name": "internal_status",
            "in": "query",
            "type": "string",
            "description": "Внутренний статус"
        },
        {
            "name": "final_status",
            "in": "query",
            "type": "string",
            "description": "Итоговый статус"
        },
        {
            "name": "registry_addition_date_from",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "Дата добавления в реестр (от)"
        },
        {
            "name": "registry_addition_date_to",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "Дата добавления в реестр (до)"
        },
        {
            "name": "registration_date_from",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "Дата регистрации (от)"
        },
        {
            "name": "registration_date_to",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "Дата регистрации (до)"
        },
        {
            "name": "manager_name",
            "in": "query",
            "type": "string",
            "description": "Имя руководителя"
        },
        {
            "name": "website",
            "in": "query",
            "type": "string",
            "description": "Веб-сайт"
        },
        {
            "name": "email",
            "in": "query",
            "type": "string",
            "description": "Email"
        },
        {
            "name": "head_organization",
            "in": "query",
            "type": "string",
            "description": "Головная организация"
        },
        {
            "name": "head_organization_inn",
            "in": "query",
            "type": "string",
            "description": "ИНН головной организации"
        },
        {
            "name": "search",
            "in": "query",
            "type": "string",
            "description": "Общий поиск по всем текстовым полям"
        },
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "default": 1,
            "description": "Номер страницы"
        },
        {
            "name": "per_page",
            "in": "query",
            "type": "integer",
            "default": 50,
            "description": "Количество записей на странице"
        },
        {
            "name": "sort_by",
            "in": "query",
            "type": "string",
            "description": "Поле для сортировки"
        },
        {
            "name": "sort_order",
            "in": "query",
            "type": "string",
            "enum": ["asc", "desc"],
            "default": "asc",
            "description": "Порядок сортировки"
        }
    ],
    "responses": {
        200: {
            "description": "Список организаций",
            "schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Organization"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "current_page": {"type": "integer"},
                    "per_page": {"type": "integer"},
                    "has_next": {"type": "boolean"},
                    "has_prev": {"type": "boolean"}
                }
            }
        }
    }
}

ORGANIZATIONS_POST_DOC = {
    "tags": ["Organizations"],
    "summary": "Создать новую организацию",
    "description": "Создает новую организацию в базе данных",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {"$ref": "#/definitions/Organization"}
        }
    ],
    "responses": {
        201: {
            "description": "Организация создана",
            "schema": {"$ref": "#/definitions/Organization"}
        },
        400: {
            "description": "Ошибка валидации",
            "schema": {"$ref": "#/definitions/Error"}
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

FINANCIAL_INDICATORS_GET_DOC = {
    "tags": ["Financial Indicators"],
    "summary": "Получить финансовые показатели",
    "description": "Возвращает финансовые показатели с возможностью фильтрации по годам и организациям",
    "parameters": [
        {
            "name": "organization_id",
            "in": "query",
            "type": "integer",
            "description": "ID организации"
        },
        {
            "name": "year",
            "in": "query",
            "type": "integer",
            "description": "Год"
        },
        {
            "name": "year_min",
            "in": "query",
            "type": "integer",
            "description": "Минимальный год"
        },
        {
            "name": "year_max",
            "in": "query",
            "type": "integer",
            "description": "Максимальный год"
        },
        {
            "name": "revenue_min",
            "in": "query",
            "type": "number",
            "description": "Минимальная выручка"
        },
        {
            "name": "revenue_max",
            "in": "query",
            "type": "number",
            "description": "Максимальная выручка"
        },
        {
            "name": "net_profit_min",
            "in": "query",
            "type": "number",
            "description": "Минимальная чистая прибыль"
        },
        {
            "name": "net_profit_max",
            "in": "query",
            "type": "number",
            "description": "Максимальная чистая прибыль"
        },
        {
            "name": "employee_count_min",
            "in": "query",
            "type": "integer",
            "description": "Минимальная численность персонала"
        },
        {
            "name": "employee_count_max",
            "in": "query",
            "type": "integer",
            "description": "Максимальная численность персонала"
        },
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "default": 1,
            "description": "Номер страницы"
        },
        {
            "name": "per_page",
            "in": "query",
            "type": "integer",
            "default": 50,
            "description": "Количество записей на странице"
        }
    ],
    "responses": {
        200: {
            "description": "Список финансовых показателей",
            "schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/FinancialIndicator"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "current_page": {"type": "integer"},
                    "per_page": {"type": "integer"},
                    "has_next": {"type": "boolean"},
                    "has_prev": {"type": "boolean"}
                }
            }
        }
    }
}

FINANCIAL_INDICATORS_POST_DOC = {
    "tags": ["Financial Indicators"],
    "summary": "Создать финансовые показатели",
    "description": "Создает новые финансовые показатели для организации",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {"$ref": "#/definitions/FinancialIndicator"}
        }
    ],
    "responses": {
        201: {
            "description": "Финансовые показатели созданы",
            "schema": {"$ref": "#/definitions/FinancialIndicator"}
        },
        400: {
            "description": "Ошибка валидации",
            "schema": {"$ref": "#/definitions/Error"}
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}

# Аналогично для остальных таблиц...
TAXES_GET_DOC = {
    "tags": ["Taxes"],
    "summary": "Получить налоговые данные",
    "description": "Возвращает налоговые данные с возможностью фильтрации по годам и организациям",
    "parameters": [
        {
            "name": "organization_id",
            "in": "query",
            "type": "integer",
            "description": "ID организации"
        },
        {
            "name": "year",
            "in": "query",
            "type": "integer",
            "description": "Год"
        },
        {
            "name": "moscow_taxes_min",
            "in": "query",
            "type": "number",
            "description": "Минимальные налоги в бюджет Москвы"
        },
        {
            "name": "moscow_taxes_max",
            "in": "query",
            "type": "number",
            "description": "Максимальные налоги в бюджет Москвы"
        },
        {
            "name": "profit_tax_min",
            "in": "query",
            "type": "number",
            "description": "Минимальный налог на прибыль"
        },
        {
            "name": "profit_tax_max",
            "in": "query",
            "type": "number",
            "description": "Максимальный налог на прибыль"
        }
    ],
    "responses": {
        200: {
            "description": "Список налоговых данных",
            "schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Tax"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "current_page": {"type": "integer"},
                    "per_page": {"type": "integer"},
                    "has_next": {"type": "boolean"},
                    "has_prev": {"type": "boolean"}
                }
            }
        }
    }
}

TAXES_POST_DOC = {
    "tags": ["Taxes"],
    "summary": "Создать налоговые данные",
    "description": "Создает новые налоговые данные для организации",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {"$ref": "#/definitions/Tax"}
        }
    ],
    "responses": {
        201: {
            "description": "Налоговые данные созданы",
            "schema": {"$ref": "#/definitions/Tax"}
        },
        400: {
            "description": "Ошибка валидации",
            "schema": {"$ref": "#/definitions/Error"}
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
}
