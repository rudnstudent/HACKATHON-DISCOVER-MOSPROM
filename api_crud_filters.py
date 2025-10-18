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

def validate_required_fields(data, model_class):
    """Проверяет обязательные поля"""
    required_fields = []
    for column in model_class.__table__.columns:
        if not column.nullable and column.name != 'id':
            required_fields.append(column.name)
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields

def create_item_from_data(model_class, data):
    """Создает объект модели из данных"""
    item_data = {}
    for column in model_class.__table__.columns:
        if column.name in data and data[column.name] is not None:
            value = data[column.name]
            
            # Обработка дат
            if 'date' in column.name.lower() and isinstance(value, str):
                try:
                    if 'T' in value:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        value = datetime.strptime(value, '%Y-%m-%d')
                except:
                    pass
            
            # Обработка булевых значений
            elif column.type.python_type == bool and isinstance(value, str):
                value = value.lower() in ['true', '1', 'yes', 'да']
            
            item_data[column.name] = value
    
    return model_class(**item_data)

def update_item_from_data(item, data):
    """Обновляет объект модели данными"""
    for column in item.__table__.columns:
        if column.name in data and column.name != 'id':
            value = data[column.name]
            
            # Обработка дат
            if 'date' in column.name.lower() and isinstance(value, str):
                try:
                    if 'T' in value:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        value = datetime.strptime(value, '%Y-%m-%d')
                except:
                    pass
            
            # Обработка булевых значений
            elif column.type.python_type == bool and isinstance(value, str):
                value = value.lower() in ['true', '1', 'yes', 'да']
            
            setattr(item, column.name, value)

def register_crud_api_routes(app):
    """Регистрирует CRUD API маршруты с поддержкой всех таблиц"""
    
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
        finally:
            session.close()
    
    @app.route('/api/tables/<table_name>/data', methods=['POST'])
    def create_table_item(table_name):
        """Создать новую запись в таблице"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        session = None
        try:
            model_class = MODELS[table_name]
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Данные не предоставлены'}), 400
            
            # Проверяем обязательные поля
            missing_fields = validate_required_fields(data, model_class)
            if missing_fields:
                return jsonify({
                    'error': 'Отсутствуют обязательные поля',
                    'missing_fields': missing_fields
                }), 400
            
            # Создаем объект
            session = db_session.create_session()
            new_item = create_item_from_data(model_class, data)
            session.add(new_item)
            session.commit()
            
            # Возвращаем созданный объект
            created_item = serialize_item(new_item, model_class)
            
            return jsonify({
                'message': 'Запись успешно создана',
                'item': created_item
            }), 201
            
        except Exception as e:
            if session:
                session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            if session:
                session.close()
    
    @app.route('/api/tables/<table_name>/data/<int:item_id>', methods=['GET'])
    def get_table_item(table_name, item_id):
        """Получить конкретную запись из таблицы"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        try:
            model_class = MODELS[table_name]
            session = db_session.create_session()
            
            item = session.query(model_class).filter(model_class.id == item_id).first()
            
            if not item:
                return jsonify({'error': 'Запись не найдена'}), 404
            
            return jsonify({
                'item': serialize_item(item, model_class)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/tables/<table_name>/data/<int:item_id>', methods=['PUT'])
    def update_table_item(table_name, item_id):
        """Обновить запись в таблице"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        session = None
        try:
            model_class = MODELS[table_name]
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Данные не предоставлены'}), 400
            
            session = db_session.create_session()
            item = session.query(model_class).filter(model_class.id == item_id).first()
            
            if not item:
                return jsonify({'error': 'Запись не найдена'}), 404
            
            # Обновляем объект
            update_item_from_data(item, data)
            session.commit()
            
            # Возвращаем обновленный объект
            updated_item = serialize_item(item, model_class)
            
            return jsonify({
                'message': 'Запись успешно обновлена',
                'item': updated_item
            })
            
        except Exception as e:
            if session:
                session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            if session:
                session.close()
    
    @app.route('/api/tables/<table_name>/data/<int:item_id>', methods=['DELETE'])
    def delete_table_item(table_name, item_id):
        """Удалить запись из таблицы"""
        if table_name not in MODELS:
            return jsonify({'error': 'Таблица не найдена'}), 404
        
        session = None
        try:
            model_class = MODELS[table_name]
            session = db_session.create_session()
            
            item = session.query(model_class).filter(model_class.id == item_id).first()
            
            if not item:
                return jsonify({'error': 'Запись не найдена'}), 404
            
            # Сохраняем данные для ответа
            deleted_item = serialize_item(item, model_class)
            
            # Удаляем объект
            session.delete(item)
            session.commit()
            
            return jsonify({
                'message': 'Запись успешно удалена',
                'deleted_item': deleted_item
            })
            
        except Exception as e:
            if session:
                session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            if session:
                session.close()
    
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
        finally:
            session.close()
    
    # Обратная совместимость - старые эндпоинты с CRUD
    @app.route('/api/organizations', methods=['GET', 'POST'])
    def organizations_crud():
        if request.method == 'GET':
            return get_table_data('organizations')
        else:  # POST
            return create_table_item('organizations')
    
    @app.route('/api/organizations/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def organization_crud(item_id):
        if request.method == 'GET':
            return get_table_item('organizations', item_id)
        elif request.method == 'PUT':
            return update_table_item('organizations', item_id)
        else:  # DELETE
            return delete_table_item('organizations', item_id)
    
    @app.route('/api/financial-indicators', methods=['GET', 'POST'])
    def financial_indicators_crud():
        if request.method == 'GET':
            return get_table_data('financial-indicators')
        else:  # POST
            return create_table_item('financial-indicators')
    
    @app.route('/api/financial-indicators/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def financial_indicator_crud(item_id):
        if request.method == 'GET':
            return get_table_item('financial-indicators', item_id)
        elif request.method == 'PUT':
            return update_table_item('financial-indicators', item_id)
        else:  # DELETE
            return delete_table_item('financial-indicators', item_id)
    
    # Создаем отдельные функции для каждой таблицы
    @app.route('/api/taxes', methods=['GET', 'POST'])
    def taxes_crud():
        if request.method == 'GET':
            return get_table_data('taxes')
        else:  # POST
            return create_table_item('taxes')
    
    @app.route('/api/taxes/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def tax_crud(item_id):
        if request.method == 'GET':
            return get_table_item('taxes', item_id)
        elif request.method == 'PUT':
            return update_table_item('taxes', item_id)
        else:  # DELETE
            return delete_table_item('taxes', item_id)
    
    @app.route('/api/contacts', methods=['GET', 'POST'])
    def contacts_crud():
        if request.method == 'GET':
            return get_table_data('contacts')
        else:  # POST
            return create_table_item('contacts')
    
    @app.route('/api/contacts/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def contact_crud(item_id):
        if request.method == 'GET':
            return get_table_item('contacts', item_id)
        elif request.method == 'PUT':
            return update_table_item('contacts', item_id)
        else:  # DELETE
            return delete_table_item('contacts', item_id)
    
    @app.route('/api/addresses', methods=['GET', 'POST'])
    def addresses_crud():
        if request.method == 'GET':
            return get_table_data('addresses')
        else:  # POST
            return create_table_item('addresses')
    
    @app.route('/api/addresses/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def address_crud(item_id):
        if request.method == 'GET':
            return get_table_item('addresses', item_id)
        elif request.method == 'PUT':
            return update_table_item('addresses', item_id)
        else:  # DELETE
            return delete_table_item('addresses', item_id)
    
    @app.route('/api/okveds', methods=['GET', 'POST'])
    def okveds_crud():
        if request.method == 'GET':
            return get_table_data('okveds')
        else:  # POST
            return create_table_item('okveds')
    
    @app.route('/api/okveds/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def okved_crud(item_id):
        if request.method == 'GET':
            return get_table_item('okveds', item_id)
        elif request.method == 'PUT':
            return update_table_item('okveds', item_id)
        else:  # DELETE
            return delete_table_item('okveds', item_id)
    
    @app.route('/api/industries', methods=['GET', 'POST'])
    def industries_crud():
        if request.method == 'GET':
            return get_table_data('industries')
        else:  # POST
            return create_table_item('industries')
    
    @app.route('/api/industries/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def industry_crud(item_id):
        if request.method == 'GET':
            return get_table_item('industries', item_id)
        elif request.method == 'PUT':
            return update_table_item('industries', item_id)
        else:  # DELETE
            return delete_table_item('industries', item_id)
    
    @app.route('/api/company-sizes', methods=['GET', 'POST'])
    def company_sizes_crud():
        if request.method == 'GET':
            return get_table_data('company-sizes')
        else:  # POST
            return create_table_item('company-sizes')
    
    @app.route('/api/company-sizes/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def company_size_crud(item_id):
        if request.method == 'GET':
            return get_table_item('company-sizes', item_id)
        elif request.method == 'PUT':
            return update_table_item('company-sizes', item_id)
        else:  # DELETE
            return delete_table_item('company-sizes', item_id)
    
    @app.route('/api/support', methods=['GET', 'POST'])
    def support_crud():
        if request.method == 'GET':
            return get_table_data('support')
        else:  # POST
            return create_table_item('support')
    
    @app.route('/api/support/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def support_item_crud(item_id):
        if request.method == 'GET':
            return get_table_item('support', item_id)
        elif request.method == 'PUT':
            return update_table_item('support', item_id)
        else:  # DELETE
            return delete_table_item('support', item_id)
    
    @app.route('/api/investment-export', methods=['GET', 'POST'])
    def investment_export_crud():
        if request.method == 'GET':
            return get_table_data('investment-export')
        else:  # POST
            return create_table_item('investment-export')
    
    @app.route('/api/investment-export/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def investment_export_item_crud(item_id):
        if request.method == 'GET':
            return get_table_item('investment-export', item_id)
        elif request.method == 'PUT':
            return update_table_item('investment-export', item_id)
        else:  # DELETE
            return delete_table_item('investment-export', item_id)
    
    @app.route('/api/property-land', methods=['GET', 'POST'])
    def property_land_crud():
        if request.method == 'GET':
            return get_table_data('property-land')
        else:  # POST
            return create_table_item('property-land')
    
    @app.route('/api/property-land/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def property_land_item_crud(item_id):
        if request.method == 'GET':
            return get_table_item('property-land', item_id)
        elif request.method == 'PUT':
            return update_table_item('property-land', item_id)
        else:  # DELETE
            return delete_table_item('property-land', item_id)
    
    @app.route('/api/production', methods=['GET', 'POST'])
    def production_crud():
        if request.method == 'GET':
            return get_table_data('production')
        else:  # POST
            return create_table_item('production')
    
    @app.route('/api/production/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def production_item_crud(item_id):
        if request.method == 'GET':
            return get_table_item('production', item_id)
        elif request.method == 'PUT':
            return update_table_item('production', item_id)
        else:  # DELETE
            return delete_table_item('production', item_id)
    
    print("CRUD API маршруты зарегистрированы:")
    print("- /api/tables - список всех таблиц")
    print("- /api/tables/<name>/columns - метаданные столбцов")
    print("- /api/tables/<name>/data - GET (список), POST (создание)")
    print("- /api/tables/<name>/data/<id> - GET, PUT, DELETE (конкретная запись)")
    print("- /api/tables/<name>/stats - статистика по таблице")
    print("\nПоддерживаемые HTTP методы:")
    print("- GET - получение данных")
    print("- POST - создание новых записей")
    print("- PUT - обновление записей")
    print("- DELETE - удаление записей")
    print("\nПоддерживаемые таблицы:")
    for table_name in MODELS.keys():
        print(f"- {table_name}")
