from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data import db_session
from flasgger import Swagger
from api_crud_filters import register_crud_api_routes
from flask_restful import Api
from functools import wraps
from flask import abort
import requests

app = Flask(__name__)

load_dotenv()

# Конфигурация с резервным секретным ключом
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 МБ максимальный размер файла

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'txt', 'doc', 'docx'}

# Создаем папку для загрузок, если она не существует
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Moscow Industry Database API",
            "description": "API для работы с базой данных промышленных предприятий Москвы",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@moscow-industry.ru"
            }
        },
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "host": "localhost:5000",
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ],
        "tags": [
            {
                "name": "Organizations",
                "description": "Операции с организациями"
            },
            {
                "name": "Financial Indicators",
                "description": "Финансовые показатели по годам"
            },
            {
                "name": "Taxes",
                "description": "Налоговые данные по годам"
            },
            {
                "name": "Contacts",
                "description": "Контактная информация"
            },
            {
                "name": "Addresses",
                "description": "Адресная информация"
            },
            {
                "name": "OKVED",
                "description": "Коды ОКВЭД"
            },
            {
                "name": "Industries",
                "description": "Отраслевая информация"
            },
            {
                "name": "Company Sizes",
                "description": "Размеры предприятий по годам"
            },
            {
                "name": "Support",
                "description": "Поддержка и статусы"
            },
            {
                "name": "Investment Export",
                "description": "Инвестиции и экспорт по годам"
            },
            {
                "name": "Property Land",
                "description": "Имущественно-земельный комплекс"
            },
            {
                "name": "Production",
                "description": "Производственная информация"
            }
        ],
        "definitions": {
            "Organization": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "inn": {"type": "string", "maxLength": 12},
                    "name": {"type": "string", "maxLength": 255},
                    "full_name": {"type": "string", "maxLength": 500},
                    "spark_status": {"type": "string", "maxLength": 100},
                    "internal_status": {"type": "string", "maxLength": 100},
                    "final_status": {"type": "string", "maxLength": 100},
                    "registry_addition_date": {"type": "string", "format": "date"},
                    "registration_date": {"type": "string", "format": "date"},
                    "manager_name": {"type": "string", "maxLength": 255},
                    "website": {"type": "string", "maxLength": 255},
                    "email": {"type": "string", "maxLength": 255},
                    "general_info": {"type": "string"},
                    "head_organization": {"type": "string", "maxLength": 255},
                    "head_organization_inn": {"type": "string", "maxLength": 12},
                    "head_organization_relation_type": {"type": "string", "maxLength": 100}
                }
            },
            "FinancialIndicator": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "revenue": {"type": "number"},
                    "net_profit": {"type": "number"},
                    "employee_count": {"type": "integer"},
                    "employee_count_moscow": {"type": "integer"},
                    "payroll_all_employees": {"type": "number"},
                    "payroll_moscow_employees": {"type": "number"},
                    "avg_salary_all_employees": {"type": "number"},
                    "avg_salary_moscow_employees": {"type": "number"}
                }
            },
            "Tax": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "moscow_taxes": {"type": "number"},
                    "profit_tax": {"type": "number"},
                    "property_tax": {"type": "number"},
                    "land_tax": {"type": "number"},
                    "personal_income_tax": {"type": "number"},
                    "transport_tax": {"type": "number"},
                    "other_taxes": {"type": "number"},
                    "excise_taxes": {"type": "number"}
                }
            },
            "Contact": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "contact_type": {"type": "string", "maxLength": 100},
                    "name": {"type": "string", "maxLength": 255},
                    "phone": {"type": "string", "maxLength": 50},
                    "email": {"type": "string", "maxLength": 255},
                    "management_email": {"type": "string", "maxLength": 255}
                }
            },
            "Address": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "address_type": {"type": "string", "maxLength": 50},
                    "full_address": {"type": "string", "maxLength": 500},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "district": {"type": "string", "maxLength": 100},
                    "area": {"type": "string", "maxLength": 100}
                }
            },
            "OKVED": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "okved_type": {"type": "string", "maxLength": 100},
                    "code": {"type": "string", "maxLength": 20},
                    "description": {"type": "string"}
                }
            },
            "Industry": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "main_industry": {"type": "string", "maxLength": 255},
                    "main_subindustry": {"type": "string", "maxLength": 255},
                    "additional_industry": {"type": "string", "maxLength": 255},
                    "additional_subindustry": {"type": "string", "maxLength": 255},
                    "industry_presentations": {"type": "string"},
                    "industry_by_spark": {"type": "string", "maxLength": 255}
                }
            },
            "CompanySize": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "size_final": {"type": "string", "maxLength": 100},
                    "size_by_employees": {"type": "string", "maxLength": 100},
                    "size_by_revenue": {"type": "string", "maxLength": 100}
                }
            },
            "Support": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "support_data": {"type": "string"},
                    "special_status": {"type": "string", "maxLength": 255},
                    "platform_final": {"type": "string", "maxLength": 100},
                    "moscow_support_received": {"type": "boolean"},
                    "system_forming_enterprise": {"type": "boolean"},
                    "sme_status": {"type": "string", "maxLength": 100}
                }
            },
            "InvestmentExport": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "moscow_investments": {"type": "number"},
                    "export_volume": {"type": "number"}
                }
            },
            "PropertyLand": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "land_cadastral_number": {"type": "string", "maxLength": 50},
                    "land_area": {"type": "number"},
                    "land_use_type": {"type": "string", "maxLength": 255},
                    "land_ownership_type": {"type": "string", "maxLength": 100},
                    "land_owner": {"type": "string", "maxLength": 255},
                    "building_cadastral_number": {"type": "string", "maxLength": 50},
                    "building_area": {"type": "number"},
                    "building_use_type": {"type": "string", "maxLength": 255},
                    "building_type_purpose": {"type": "string", "maxLength": 255},
                    "building_ownership_type": {"type": "string", "maxLength": 100},
                    "building_owner": {"type": "string", "maxLength": 255},
                    "production_area": {"type": "number"}
                }
            },
            "Production": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "manufactured_products": {"type": "string"},
                    "standardized_products": {"type": "string"},
                    "product_names": {"type": "string"},
                    "okpd2_products": {"type": "string"},
                    "product_types_segments": {"type": "string"},
                    "product_catalog": {"type": "string"},
                    "government_order": {"type": "boolean"},
                    "production_capacity_utilization": {"type": "string", "maxLength": 100},
                    "export_supplies": {"type": "boolean"},
                    "export_volume_previous_year": {"type": "number"},
                    "export_countries": {"type": "string"},
                    "tn_ved_code": {"type": "string", "maxLength": 50}
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"}
                }
            }
        }
    })

# Инициализация API будет выполнена в register_api_routes

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "db/database_test.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)

# Инициализация базы данных
init_db()

# Регистрация API маршрутов
register_crud_api_routes(app)


def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загрузки файла с улучшенной валидацией"""
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            return render_template('index.html', error='Файл не выбран')

        file = request.files['file']

        # Если пользователь не выбрал файл
        if file.filename == '':
            return render_template('index.html', error='Файл не выбран')

        # Проверяем расширение файла
        if not allowed_file(file.filename):
            return render_template('index.html', error='Неверный формат файла. Разрешены только CSV, XLSX, XLS, PDF, TXT, DOC, DOCX файлы.')

        # Если файл валиден, сохраняем его
        if file:
            # Безопасное имя файла
            filename = secure_filename(file.filename)

            # Генерируем уникальное имя, если файл уже существует
            base_filename, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base_filename}_{counter}{extension}"
                counter += 1

            # Сохраняем файл
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Получаем размер файла
            file_size = os.path.getsize(filepath)
            file_size_mb = round(file_size / (1024 * 1024), 2)

            return render_template('index.html', 
                                 success=f'Файл "{filename}" успешно загружен! Размер: {file_size_mb} МБ')

    except RequestEntityTooLarge:
        return render_template('index.html', error='Файл слишком большой. Максимальный размер: 16 МБ')
    except Exception as e:
        return render_template('index.html', error=f'Произошла ошибка при загрузке файла: {str(e)}')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница контактов с формой"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Здесь можно добавить логику сохранения сообщения
        return render_template('contact.html', 
                             success=True, 
                             name=name)
    
    return render_template('contact.html')


@app.route('/about')
def about():
    """Страница о проекте"""
    return render_template('about.html')


@app.route('/api/docs')
def api_docs():
    """Swagger UI документация"""
    return redirect('/apidocs/')

@app.route('/api/test')
def api_test():
    """Страница тестирования API"""
    return render_template('api_test.html')

@app.route('/filter')
def filter_page():
    """Страница фильтрации таблицы организаций"""
    return render_template('filter_api.html')

@app.route('/dynamic-filter')
def dynamic_filter_page():
    """Динамическая страница фильтрации для всех таблиц"""
    return render_template('dynamic_filter.html')

@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    return render_template('500.html'), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Обработчик ошибки 413 - слишком большой файл"""
    return render_template('index.html', error='Файл слишком большой. Максимальный размер: 16 МБ'), 413


if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data import db_session
from flasgger import Swagger
from api_dynamic_filters import register_dynamic_api_routes
from flask_restful import Api
from functools import wraps
from flask import abort
import requests

app = Flask(__name__)

load_dotenv()

# Конфигурация с резервным секретным ключом
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 МБ максимальный размер файла

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'txt', 'doc', 'docx'}

# Создаем папку для загрузок, если она не существует
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Moscow Industry Database API",
            "description": "API для работы с базой данных промышленных предприятий Москвы",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@moscow-industry.ru"
            }
        },
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "host": "localhost:5000",
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ],
        "tags": [
            {
                "name": "Organizations",
                "description": "Операции с организациями"
            },
            {
                "name": "Financial Indicators",
                "description": "Финансовые показатели по годам"
            },
            {
                "name": "Taxes",
                "description": "Налоговые данные по годам"
            },
            {
                "name": "Contacts",
                "description": "Контактная информация"
            },
            {
                "name": "Addresses",
                "description": "Адресная информация"
            },
            {
                "name": "OKVED",
                "description": "Коды ОКВЭД"
            },
            {
                "name": "Industries",
                "description": "Отраслевая информация"
            },
            {
                "name": "Company Sizes",
                "description": "Размеры предприятий по годам"
            },
            {
                "name": "Support",
                "description": "Поддержка и статусы"
            },
            {
                "name": "Investment Export",
                "description": "Инвестиции и экспорт по годам"
            },
            {
                "name": "Property Land",
                "description": "Имущественно-земельный комплекс"
            },
            {
                "name": "Production",
                "description": "Производственная информация"
            }
        ],
        "definitions": {
            "Organization": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "inn": {"type": "string", "maxLength": 12},
                    "name": {"type": "string", "maxLength": 255},
                    "full_name": {"type": "string", "maxLength": 500},
                    "spark_status": {"type": "string", "maxLength": 100},
                    "internal_status": {"type": "string", "maxLength": 100},
                    "final_status": {"type": "string", "maxLength": 100},
                    "registry_addition_date": {"type": "string", "format": "date"},
                    "registration_date": {"type": "string", "format": "date"},
                    "manager_name": {"type": "string", "maxLength": 255},
                    "website": {"type": "string", "maxLength": 255},
                    "email": {"type": "string", "maxLength": 255},
                    "general_info": {"type": "string"},
                    "head_organization": {"type": "string", "maxLength": 255},
                    "head_organization_inn": {"type": "string", "maxLength": 12},
                    "head_organization_relation_type": {"type": "string", "maxLength": 100}
                }
            },
            "FinancialIndicator": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "revenue": {"type": "number"},
                    "net_profit": {"type": "number"},
                    "employee_count": {"type": "integer"},
                    "employee_count_moscow": {"type": "integer"},
                    "payroll_all_employees": {"type": "number"},
                    "payroll_moscow_employees": {"type": "number"},
                    "avg_salary_all_employees": {"type": "number"},
                    "avg_salary_moscow_employees": {"type": "number"}
                }
            },
            "Tax": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "moscow_taxes": {"type": "number"},
                    "profit_tax": {"type": "number"},
                    "property_tax": {"type": "number"},
                    "land_tax": {"type": "number"},
                    "personal_income_tax": {"type": "number"},
                    "transport_tax": {"type": "number"},
                    "other_taxes": {"type": "number"},
                    "excise_taxes": {"type": "number"}
                }
            },
            "Contact": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "contact_type": {"type": "string", "maxLength": 100},
                    "name": {"type": "string", "maxLength": 255},
                    "phone": {"type": "string", "maxLength": 50},
                    "email": {"type": "string", "maxLength": 255},
                    "management_email": {"type": "string", "maxLength": 255}
                }
            },
            "Address": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "address_type": {"type": "string", "maxLength": 50},
                    "full_address": {"type": "string", "maxLength": 500},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "district": {"type": "string", "maxLength": 100},
                    "area": {"type": "string", "maxLength": 100}
                }
            },
            "OKVED": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "okved_type": {"type": "string", "maxLength": 100},
                    "code": {"type": "string", "maxLength": 20},
                    "description": {"type": "string"}
                }
            },
            "Industry": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "main_industry": {"type": "string", "maxLength": 255},
                    "main_subindustry": {"type": "string", "maxLength": 255},
                    "additional_industry": {"type": "string", "maxLength": 255},
                    "additional_subindustry": {"type": "string", "maxLength": 255},
                    "industry_presentations": {"type": "string"},
                    "industry_by_spark": {"type": "string", "maxLength": 255}
                }
            },
            "CompanySize": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "size_final": {"type": "string", "maxLength": 100},
                    "size_by_employees": {"type": "string", "maxLength": 100},
                    "size_by_revenue": {"type": "string", "maxLength": 100}
                }
            },
            "Support": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "support_data": {"type": "string"},
                    "special_status": {"type": "string", "maxLength": 255},
                    "platform_final": {"type": "string", "maxLength": 100},
                    "moscow_support_received": {"type": "boolean"},
                    "system_forming_enterprise": {"type": "boolean"},
                    "sme_status": {"type": "string", "maxLength": 100}
                }
            },
            "InvestmentExport": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "year": {"type": "integer"},
                    "moscow_investments": {"type": "number"},
                    "export_volume": {"type": "number"}
                }
            },
            "PropertyLand": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "land_cadastral_number": {"type": "string", "maxLength": 50},
                    "land_area": {"type": "number"},
                    "land_use_type": {"type": "string", "maxLength": 255},
                    "land_ownership_type": {"type": "string", "maxLength": 100},
                    "land_owner": {"type": "string", "maxLength": 255},
                    "building_cadastral_number": {"type": "string", "maxLength": 50},
                    "building_area": {"type": "number"},
                    "building_use_type": {"type": "string", "maxLength": 255},
                    "building_type_purpose": {"type": "string", "maxLength": 255},
                    "building_ownership_type": {"type": "string", "maxLength": 100},
                    "building_owner": {"type": "string", "maxLength": 255},
                    "production_area": {"type": "number"}
                }
            },
            "Production": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "organization_id": {"type": "integer"},
                    "manufactured_products": {"type": "string"},
                    "standardized_products": {"type": "string"},
                    "product_names": {"type": "string"},
                    "okpd2_products": {"type": "string"},
                    "product_types_segments": {"type": "string"},
                    "product_catalog": {"type": "string"},
                    "government_order": {"type": "boolean"},
                    "production_capacity_utilization": {"type": "string", "maxLength": 100},
                    "export_supplies": {"type": "boolean"},
                    "export_volume_previous_year": {"type": "number"},
                    "export_countries": {"type": "string"},
                    "tn_ved_code": {"type": "string", "maxLength": 50}
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"}
                }
            }
        }
    })

# Инициализация API будет выполнена в register_api_routes

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "db/database_test.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)

# Инициализация базы данных
init_db()

# Регистрация API маршрутов
register_dynamic_api_routes(app)


def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загрузки файла с улучшенной валидацией"""
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            return render_template('index.html', error='Файл не выбран')

        file = request.files['file']

        # Если пользователь не выбрал файл
        if file.filename == '':
            return render_template('index.html', error='Файл не выбран')

        # Проверяем расширение файла
        if not allowed_file(file.filename):
            return render_template('index.html', error='Неверный формат файла. Разрешены только CSV, XLSX, XLS, PDF, TXT, DOC, DOCX файлы.')

        # Если файл валиден, сохраняем его
        if file:
            # Безопасное имя файла
            filename = secure_filename(file.filename)

            # Генерируем уникальное имя, если файл уже существует
            base_filename, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base_filename}_{counter}{extension}"
                counter += 1

            # Сохраняем файл
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Получаем размер файла
            file_size = os.path.getsize(filepath)
            file_size_mb = round(file_size / (1024 * 1024), 2)

            return render_template('index.html', 
                                 success=f'Файл "{filename}" успешно загружен! Размер: {file_size_mb} МБ')

    except RequestEntityTooLarge:
        return render_template('index.html', error='Файл слишком большой. Максимальный размер: 16 МБ')
    except Exception as e:
        return render_template('index.html', error=f'Произошла ошибка при загрузке файла: {str(e)}')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница контактов с формой"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Здесь можно добавить логику сохранения сообщения
        return render_template('contact.html', 
                             success=True, 
                             name=name)
    
    return render_template('contact.html')


@app.route('/about')
def about():
    """Страница о проекте"""
    return render_template('about.html')


@app.route('/api/docs')
def api_docs():
    """Swagger UI документация"""
    return redirect('/apidocs/')


@app.route('/api/test')
def api_test():
    """Страница тестирования API"""
    return render_template('api_test.html')


@app.route('/filter')
def filter_page():
    """Страница фильтрации таблицы организаций"""
    return render_template('filter_api.html')


@app.route('/dynamic-filter')
def dynamic_filter_page():
    """Динамическая страница фильтрации для всех таблиц"""
    return render_template('dynamic_filter.html')


@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    return render_template('500.html'), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Обработчик ошибки 413 - слишком большой файл"""
    return render_template('index.html', error='Файл слишком большой. Максимальный размер: 16 МБ'), 413


if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
>>>>>>> 4c8dd5532cdc63fdf5d515471200fbc696eceb35
