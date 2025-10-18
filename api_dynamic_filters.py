from flask import jsonify, request
from data import db_session
from data.organization import Organization
from data.FinancialIndicator import FinancialIndicator
from data.Tax import Tax
from data.adresses import Address
from data.Okved import Okved
from data.Contact import Contact
from data.Industry import Industry
from data.CompanySize import CompanySize
from data.Support import Support
from data.InvestmentExport import InvestmentExport
from data.PropertyLand import PropertyLand
from data.Production import Production
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime
import json

# Словарь всех моделей для динамической работы
MODELS = {
    'organizations': Organization,
    'financial-indicators': FinancialIndicator,
    'taxes': Tax,
    'addresses': Address,
    'okveds': Okved,
    'contacts': Contact,
    'industries': Industry,
    'company-sizes': CompanySize,
    'support': Support,
    'investment-export': InvestmentExport,
    'property-land': PropertyLand,
    'production': Production
}

def get_column_metadata(model_class):
    """Получает метаданные о столбцах модели"""
    metadata = []
    for column in model_class.__table__.columns:
        if column.name == 'id':
            continue
            
        column_info = {
            'name': column.name,
            'type': str(column.type),
            'python_type': column.type.python_type.__name__,
            'nullable': column.nullable,
            'max_length': getattr(column.type, 'length', None)
        }
        
        # Определяем тип фильтрации
        if column.type.python_type in [int, float]:
            column_info['filter_type'] = 'numeric'
            column_info['supports_range'] = True
            column_info['supports_exact'] = True
            column_info['supports_like'] = False
        elif column.type.python_type == str:
            column_info['filter_type'] = 'text'
            column_info['supports_range'] = False
            column_info['supports_exact'] = True
            column_info['supports_like'] = True
        elif 'date' in column.name.lower() or 'Date' in str(column.type):
            column_info['filter_type'] = 'date'
            column_info['supports_range'] = True
            column_info['supports_exact'] = True
            column_info['supports_like'] = False
        elif column.type.python_type == bool:
            column_info['filter_type'] = 'boolean'
            column_info['supports_range'] = False
            column_info['supports_exact'] = True
            column_info['supports_like'] = False
        else:
            column_info['filter_type'] = 'other'
            column_info['supports_range'] = False
            column_info['supports_exact'] = True
            column_info['supports_like'] = False
            
        metadata.append(column_info)
    
    return metadata

def apply_filters_to_query(query, model_class, args):
    """Применяет фильтры к запросу с учетом типов данных"""
    for column in model_class.__table__.columns:
        if column.name == 'id':
            continue
            
        column_name = column.name
        
        # Точное значение
        if args.get(column_name) is not None:
            value = args[column_name]
            if value != '' and value is not None:
                query = query.filter(getattr(model_class, column_name) == value)
        
        # Диапазон для числовых полей
        if column.type.python_type in [int, float]:
            if args.get(f'{column_name}_min') is not None:
                min_val = args[f'{column_name}_min']
                if min_val != '' and min_val is not None:
                    query = query.filter(getattr(model_class, column_name) >= float(min_val))
            if args.get(f'{column_name}_max') is not None:
                max_val = args[f'{column_name}_max']
                if max_val != '' and max_val is not None:
                    query = query.filter(getattr(model_class, column_name) <= float(max_val))
        
        # Поиск по подстроке для строковых полей
        elif column.type.python_type == str:
            if args.get(f'{column_name}_like') is not None:
                like_val = args[f'{column_name}_like']
                if like_val != '' and like_val is not None:
                    query = query.filter(getattr(model_class, column_name).like(f"%{like_val}%"))
        
        # Фильтрация по датам
        elif 'date' in column_name.lower():
            if args.get(f'{column_name}_from') is not None:
                from_val = args[f'{column_name}_from']
                if from_val != '' and from_val is not None:
                    try:
                        from_date = datetime.strptime(from_val, '%Y-%m-%d')
                        query = query.filter(getattr(model_class, column_name) >= from_date)
                    except ValueError:
                        pass
            if args.get(f'{column_name}_to') is not None:
                to_val = args[f'{column_name}_to']
                if to_val != '' and to_val is not None:
                    try:
                        to_date = datetime.strptime(to_val, '%Y-%m-%d')
                        query = query.filter(getattr(model_class, column_name) <= to_date)
                    except ValueError:
                        pass
    
    # Общий поиск по всем текстовым полям
    if args.get('search'):
        search_term = f"%{args['search']}%"
        search_conditions = []
        for column in model_class.__table__.columns:
            if column.type.python_type == str:
                search_conditions.append(getattr(model_class, column.name).like(search_term))
        if search_conditions:
            query = query.filter(or_(*search_conditions))
    
    return query

def apply_sorting_to_query(query, model_class, args):
    """Применяет сортировку к запросу"""
    if args.get('sort_by'):
        sort_field = args['sort_by']
        if hasattr(model_class, sort_field):
            sort_column = getattr(model_class, sort_field)
            if args.get('sort_order') == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
    return query

def serialize_item(item, model_class):
    """Сериализует объект модели в словарь"""
    item_dict = {}
    for column in model_class.__table__.columns:
        value = getattr(item, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        elif value is not None and 'date' in column.name.lower():
            # Обработка строковых дат
            try:
                if isinstance(value, str) and value.strip():
                    parsed_date = datetime.strptime(value, '%Y-%m-%d')
                    value = parsed_date.isoformat()
            except:
                pass
        item_dict[column.name] = value
    return item_dict

def register_dynamic_api_routes(app):
    """Регистрирует динамические API маршруты с поддержкой всех таблиц"""
    
    @app.route('/api/tables', methods=['GET'])
    def get_available_tables():
        """Получить список доступных таблиц"""
        tables = []
        for table_name, model_class in MODELS.items():
            table_info = {
                'name': table_name,
                'display_name': model_class.__name__,
                'description': f'Таблица {model_class.__name__}',
                'columns_count': len([c for c in model_class.__table__.columns if c.name != 'id'])
            }
            tables.append(table_info)
        
        return jsonify({
            'tables': tables,
            'total': len(tables)
        })
    
    @app.route('/api/tables/<table_name>/columns', methods=['GET'])
    def get_table_columns(table_name):
        """Получить метаданные столбцов для конкретной таблицы"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        model_class = MODELS[table_name]
        columns = get_column_metadata(model_class)
        
        return jsonify({
            'table_name': table_name,
            'model_name': model_class.__name__,
            'columns': columns,
            'total_columns': len(columns)
        })
    
    @app.route('/api/tables/<table_name>/data', methods=['GET'])
    def get_table_data(table_name):
        """Получить данные из таблицы с фильтрацией"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        try:
            model_class = MODELS[table_name]
            session = db_session.create_session()
            
            # Параметры пагинации
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            # Параметры фильтрации и сортировки
            args = request.args.to_dict()
            
            # Запрос с фильтрацией
            query = session.query(model_class)
            query = apply_filters_to_query(query, model_class, args)
            query = apply_sorting_to_query(query, model_class, args)
            
            # Получаем общее количество записей
            total = query.count()
            
            # Вычисляем пагинацию
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            # Преобразуем в словари
            items = [serialize_item(item, model_class) for item in items_query]
            
            # Вычисляем метаданные пагинации
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            # Получаем метаданные столбцов
            columns_metadata = get_column_metadata(model_class)
            
            return jsonify({
                'table_name': table_name,
                'model_name': model_class.__name__,
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'columns_metadata': columns_metadata,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tables/<table_name>/stats', methods=['GET'])
    def get_table_stats(table_name):
        """Получить статистику по таблице"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        try:
            model_class = MODELS[table_name]
            session = db_session.create_session()
            
            # Общее количество записей
            total_records = session.query(model_class).count()
            
            # Статистика по числовым полям
            numeric_stats = {}
            for column in model_class.__table__.columns:
                if column.type.python_type in [int, float]:
                    try:
                        min_val = session.query(getattr(model_class, column.name)).filter(
                            getattr(model_class, column.name).isnot(None)
                        ).order_by(asc(getattr(model_class, column.name))).first()[0]
                        
                        max_val = session.query(getattr(model_class, column.name)).filter(
                            getattr(model_class, column.name).isnot(None)
                        ).order_by(desc(getattr(model_class, column.name))).first()[0]
                        
                        numeric_stats[column.name] = {
                            'min': min_val,
                            'max': max_val,
                            'type': column.type.python_type.__name__
                        }
                    except:
                        pass
            
            # Уникальные значения для строковых полей (первые 100)
            text_values = {}
            for column in model_class.__table__.columns:
                if column.type.python_type == str and column.name != 'id':
                    try:
                        unique_values = session.query(getattr(model_class, column.name)).filter(
                            getattr(model_class, column.name).isnot(None),
                            getattr(model_class, column.name) != ''
                        ).distinct().limit(100).all()
                        text_values[column.name] = [v[0] for v in unique_values]
                    except:
                        pass
            
            return jsonify({
                'table_name': table_name,
                'total_records': total_records,
                'numeric_stats': numeric_stats,
                'text_values': text_values
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Обратная совместимость - старые эндпоинты
    @app.route('/api/organizations', methods=['GET'])
    def get_organizations():
        return get_table_data('organizations')
    
    @app.route('/api/financial-indicators', methods=['GET'])
    def get_financial_indicators():
        return get_table_data('financial-indicators')
    
    @app.route('/api/taxes', methods=['GET'])
    def get_taxes():
        return get_table_data('taxes')
    
    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        return get_table_data('contacts')
    
    @app.route('/api/addresses', methods=['GET'])
    def get_addresses():
        return get_table_data('addresses')
    
    @app.route('/api/okveds', methods=['GET'])
    def get_okveds():
        return get_table_data('okveds')
    
    @app.route('/api/industries', methods=['GET'])
    def get_industries():
        return get_table_data('industries')
    
    @app.route('/api/company-sizes', methods=['GET'])
    def get_company_sizes():
        return get_table_data('company-sizes')
    
    @app.route('/api/support', methods=['GET'])
    def get_support():
        return get_table_data('support')
    
    @app.route('/api/investment-export', methods=['GET'])
    def get_investment_export():
        return get_table_data('investment-export')
    
    @app.route('/api/property-land', methods=['GET'])
    def get_property_land():
        return get_table_data('property-land')
    
    @app.route('/api/production', methods=['GET'])
    def get_production():
        return get_table_data('production')
    
    print("Динамические API маршруты зарегистрированы:")
    print("- /api/tables - список всех таблиц")
    print("- /api/tables/<name>/columns - метаданные столбцов")
    print("- /api/tables/<name>/data - данные с фильтрацией")
    print("- /api/tables/<name>/stats - статистика по таблице")
    print("\nПоддерживаемые таблицы:")
    for table_name in MODELS.keys():
        print(f"- {table_name}")
