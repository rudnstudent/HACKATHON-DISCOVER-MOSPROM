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

def apply_filters_to_query(query, model_class, args):
    """Применяет фильтры к запросу"""
    for column in model_class.__table__.columns:
        if column.name == 'id':
            continue
            
        column_name = column.name
        
        # Точное значение
        if args.get(column_name) is not None:
            query = query.filter(getattr(model_class, column_name) == args[column_name])
        
        # Диапазон для числовых полей
        if column.type.python_type in [int, float]:
            if args.get(f'{column_name}_min') is not None:
                query = query.filter(getattr(model_class, column_name) >= args[f'{column_name}_min'])
            if args.get(f'{column_name}_max') is not None:
                query = query.filter(getattr(model_class, column_name) <= args[f'{column_name}_max'])
        
        # Поиск по подстроке для строковых полей
        elif column.type.python_type == str:
            if args.get(f'{column_name}_like') is not None:
                query = query.filter(getattr(model_class, column_name).like(f"%{args[f'{column_name}_like']}%"))
    
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

def register_api_routes_with_filters(app):
    """Регистрирует API маршруты с поддержкой фильтрации"""
    
    @app.route('/api/organizations', methods=['GET'])
    def get_organizations():
        """Получить список организаций с фильтрацией"""
        try:
            session = db_session.create_session()
            
            # Параметры пагинации
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            # Параметры фильтрации и сортировки
            args = request.args.to_dict()
            
            # Запрос с фильтрацией
            query = session.query(Organization)
            query = apply_filters_to_query(query, Organization, args)
            query = apply_sorting_to_query(query, Organization, args)
            
            # Получаем общее количество записей
            total = query.count()
            
            # Вычисляем пагинацию
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            # Преобразуем в словари
            items = [serialize_item(item, Organization) for item in items_query]
            
            # Вычисляем метаданные пагинации
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/financial-indicators', methods=['GET'])
    def get_financial_indicators():
        """Получить список финансовых показателей с фильтрацией"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            args = request.args.to_dict()
            
            query = session.query(FinancialIndicator)
            query = apply_filters_to_query(query, FinancialIndicator, args)
            query = apply_sorting_to_query(query, FinancialIndicator, args)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = [serialize_item(item, FinancialIndicator) for item in items_query]
            
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/taxes', methods=['GET'])
    def get_taxes():
        """Получить список налоговых данных с фильтрацией"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            args = request.args.to_dict()
            
            query = session.query(Tax)
            query = apply_filters_to_query(query, Tax, args)
            query = apply_sorting_to_query(query, Tax, args)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = [serialize_item(item, Tax) for item in items_query]
            
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        """Получить список контактов с фильтрацией"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            args = request.args.to_dict()
            
            query = session.query(Contact)
            query = apply_filters_to_query(query, Contact, args)
            query = apply_sorting_to_query(query, Contact, args)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = [serialize_item(item, Contact) for item in items_query]
            
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/addresses', methods=['GET'])
    def get_addresses():
        """Получить список адресов с фильтрацией"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            args = request.args.to_dict()
            
            query = session.query(Address)
            query = apply_filters_to_query(query, Address, args)
            query = apply_sorting_to_query(query, Address, args)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = [serialize_item(item, Address) for item in items_query]
            
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Дополнительные эндпоинты для остальных моделей
    @app.route('/api/okveds', methods=['GET'])
    def get_okveds():
        """Получить список ОКВЭД с фильтрацией"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            args = request.args.to_dict()
            
            query = session.query(Okved)
            query = apply_filters_to_query(query, Okved, args)
            query = apply_sorting_to_query(query, Okved, args)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = [serialize_item(item, Okved) for item in items_query]
            
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return jsonify({
                'items': items,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev,
                'filters_applied': {k: v for k, v in args.items() if k not in ['page', 'per_page', 'sort_by', 'sort_order']}
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # print("API маршруты с фильтрацией зарегистрированы:")
    # print("- /api/organizations - с фильтрацией по всем полям")
    # print("- /api/financial-indicators - с фильтрацией по всем полям")
    # print("- /api/taxes - с фильтрацией по всем полям")
    # print("- /api/contacts - с фильтрацией по всем полям")
    # print("- /api/addresses - с фильтрацией по всем полям")
    # print("- /api/okveds - с фильтрацией по всем полям")
    # print("\nПоддерживаемые типы фильтрации:")
    # print("- Точное значение: ?field=value")
    # print("- Диапазон (числа): ?field_min=10&field_max=100")
    # print("- Поиск по подстроке: ?field_like=text")
    # print("- Общий поиск: ?search=text")
    # print("- Сортировка: ?sort_by=field&sort_order=asc|desc")
    # print("- Пагинация: ?page=1&per_page=50")
