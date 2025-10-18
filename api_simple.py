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

def register_simple_api_routes(app):
    """Регистрирует простые API маршруты"""
    
    @app.route('/api/organizations', methods=['GET'])
    def get_organizations():
        """Получить список организаций"""
        try:
            session = db_session.create_session()
            
            # Параметры пагинации
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            # Запрос с пагинацией
            query = session.query(Organization)
            
            # Получаем общее количество записей
            total = query.count()
            
            # Вычисляем пагинацию
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            # Преобразуем в словари
            items = []
            for item in items_query:
                item_dict = {}
                for column in Organization.__table__.columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif value is not None and 'date' in column.name.lower():
                        # Обработка строковых дат
                        try:
                            if isinstance(value, str) and value.strip():
                                # Попытка парсинга даты
                                parsed_date = datetime.strptime(value, '%Y-%m-%d')
                                value = parsed_date.isoformat()
                        except:
                            # Если не удается распарсить, оставляем как есть
                            pass
                    item_dict[column.name] = value
                items.append(item_dict)
            
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
                'has_prev': has_prev
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/financial-indicators', methods=['GET'])
    def get_financial_indicators():
        """Получить список финансовых показателей"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            query = session.query(FinancialIndicator)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = []
            for item in items_query:
                item_dict = {}
                for column in FinancialIndicator.__table__.columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item_dict[column.name] = value
                items.append(item_dict)
            
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
                'has_prev': has_prev
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/taxes', methods=['GET'])
    def get_taxes():
        """Получить список налоговых данных"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            query = session.query(Tax)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = []
            for item in items_query:
                item_dict = {}
                for column in Tax.__table__.columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item_dict[column.name] = value
                items.append(item_dict)
            
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
                'has_prev': has_prev
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        """Получить список контактов"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            query = session.query(Contact)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = []
            for item in items_query:
                item_dict = {}
                for column in Contact.__table__.columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item_dict[column.name] = value
                items.append(item_dict)
            
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
                'has_prev': has_prev
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/addresses', methods=['GET'])
    def get_addresses():
        """Получить список адресов"""
        try:
            session = db_session.create_session()
            
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 1000)
            
            query = session.query(Address)
            
            total = query.count()
            offset = (page - 1) * per_page
            items_query = query.offset(offset).limit(per_page)
            
            items = []
            for item in items_query:
                item_dict = {}
                for column in Address.__table__.columns:
                    value = getattr(item, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item_dict[column.name] = value
                items.append(item_dict)
            
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
                'has_prev': has_prev
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("Простые API маршруты зарегистрированы:")
    print("- /api/organizations")
    print("- /api/financial-indicators")
    print("- /api/taxes")
    print("- /api/contacts")
    print("- /api/addresses")
