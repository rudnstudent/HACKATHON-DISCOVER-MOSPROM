from flask_restful import Resource, Api, reqparse, abort
from flask import request, jsonify
from data import db_session
from flasgger import swag_from
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

# Инициализация API
api = Api()

def create_filter_parser(model_class):
    """Создает парсер для фильтрации по всем полям модели"""
    parser = reqparse.RequestParser()
    
    # Добавляем все поля модели как параметры фильтрации
    for column in model_class.__table__.columns:
        if column.name == 'id':
            continue
            
        # Для числовых полей добавляем диапазон фильтрации
        if column.type.python_type in [int, float]:
            parser.add_argument(f'{column.name}_min', type=column.type.python_type, help=f'Минимальное значение для {column.name}')
            parser.add_argument(f'{column.name}_max', type=column.type.python_type, help=f'Максимальное значение для {column.name}')
            parser.add_argument(f'{column.name}', type=column.type.python_type, help=f'Точное значение для {column.name}')
        # Для строковых полей добавляем поиск
        elif column.type.python_type == str:
            parser.add_argument(f'{column.name}_like', type=str, help=f'Поиск по подстроке в {column.name}')
            parser.add_argument(f'{column.name}', type=str, help=f'Точное значение для {column.name}')
        # Для дат добавляем диапазон
        elif 'date' in column.name.lower():
            parser.add_argument(f'{column.name}_from', type=str, help=f'Дата от для {column.name}')
            parser.add_argument(f'{column.name}_to', type=str, help=f'Дата до для {column.name}')
            parser.add_argument(f'{column.name}', type=str, help=f'Точная дата для {column.name}')
        # Для булевых полей
        elif column.type.python_type == bool:
            parser.add_argument(f'{column.name}', type=bool, help=f'Значение для {column.name}')
    
    # Общие параметры пагинации и сортировки
    parser.add_argument('page', type=int, default=1, help='Номер страницы')
    parser.add_argument('per_page', type=int, default=50, help='Количество записей на странице')
    parser.add_argument('sort_by', type=str, help='Поле для сортировки')
    parser.add_argument('sort_order', type=str, choices=['asc', 'desc'], default='asc', help='Порядок сортировки')
    parser.add_argument('search', type=str, help='Общий поиск по всем текстовым полям')
    
    return parser

def apply_filters(query, model_class, args):
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

def apply_sorting(query, model_class, args):
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

def apply_pagination(query, args):
    """Применяет пагинацию к запросу"""
    page = args.get('page', 1)
    per_page = min(args.get('per_page', 50), 1000)  # Максимум 1000 записей на страницу
    
    return query.paginate(page=page, per_page=per_page, error_out=False)

# Базовый класс для API ресурсов
class BaseAPI(Resource):
    def __init__(self):
        self.model_class = None
        self.parser = None
    
    def get(self):
        """Получить список записей с фильтрацией"""
        if not self.model_class:
            abort(500, message="Model class not defined")
        
        args = self.parser.parse_args()
        query = self.model_class.query
        
        # Применяем фильтры
        query = apply_filters(query, self.model_class, args)
        
        # Применяем сортировку
        query = apply_sorting(query, self.model_class, args)
        
        # Применяем пагинацию
        paginated_query = apply_pagination(query, args)
        
        # Преобразуем в словари
        items = []
        for item in paginated_query.items:
            item_dict = {}
            for column in self.model_class.__table__.columns:
                value = getattr(item, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                item_dict[column.name] = value
            items.append(item_dict)
        
        return {
            'items': items,
            'total': paginated_query.total,
            'pages': paginated_query.pages,
            'current_page': paginated_query.page,
            'per_page': paginated_query.per_page,
            'has_next': paginated_query.has_next,
            'has_prev': paginated_query.has_prev
        }

    def post(self):
        """Создать новую запись"""
        if not self.model_class:
            abort(500, message="Model class not defined")
        
        data = request.get_json()
        if not data:
            abort(400, message="No data provided")
        
        try:
            # Создаем новую запись
            new_item = self.model_class()
            for key, value in data.items():
                if hasattr(new_item, key):
                    setattr(new_item, key, value)
            
            db_session.create_session().add(new_item)
            db_session.create_session().commit()
            
            # Возвращаем созданную запись
            item_dict = {}
            for column in self.model_class.__table__.columns:
                value = getattr(new_item, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                item_dict[column.name] = value
            
            return item_dict, 201
            
        except Exception as e:
            db_session.create_session().rollback()
            abort(500, message=f"Error creating record: {str(e)}")

# API ресурсы для каждой таблицы
class OrganizationListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Organization
        self.parser = create_filter_parser(Organization)
    
    @swag_from('swagger_docs.py', endpoint='organizations_get')
    def get(self):
        return super().get()
    
    @swag_from('swagger_docs.py', endpoint='organizations_post')
    def post(self):
        return super().post()

class FinancialIndicatorListAPI(BaseAPI):
    def __init__(self):
        self.model_class = FinancialIndicator
        self.parser = create_filter_parser(FinancialIndicator)
    
    @swag_from('swagger_docs.py', endpoint='financial_indicators_get')
    def get(self):
        return super().get()
    
    @swag_from('swagger_docs.py', endpoint='financial_indicators_post')
    def post(self):
        return super().post()

class TaxListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Tax
        self.parser = create_filter_parser(Tax)
    
    @swag_from('swagger_docs.py', endpoint='taxes_get')
    def get(self):
        return super().get()
    
    @swag_from('swagger_docs.py', endpoint='taxes_post')
    def post(self):
        return super().post()

class ContactListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Contact
        self.parser = create_filter_parser(Contact)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class AddressListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Address
        self.parser = create_filter_parser(Address)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class OkvedListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Okved
        self.parser = create_filter_parser(Okved)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class IndustryListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Industry
        self.parser = create_filter_parser(Industry)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class CompanySizeListAPI(BaseAPI):
    def __init__(self):
        self.model_class = CompanySize
        self.parser = create_filter_parser(CompanySize)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class SupportListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Support
        self.parser = create_filter_parser(Support)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class InvestmentExportListAPI(BaseAPI):
    def __init__(self):
        self.model_class = InvestmentExport
        self.parser = create_filter_parser(InvestmentExport)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class PropertyLandListAPI(BaseAPI):
    def __init__(self):
        self.model_class = PropertyLand
        self.parser = create_filter_parser(PropertyLand)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

class ProductionListAPI(BaseAPI):
    def __init__(self):
        self.model_class = Production
        self.parser = create_filter_parser(Production)
    
    def get(self):
        return super().get()
    
    def post(self):
        return super().post()

# Регистрация маршрутов
def register_api_routes(app):
    """Регистрирует все API маршруты"""
    api.init_app(app)
    
    # Основные маршруты для списков
    api.add_resource(OrganizationListAPI, '/api/organizations')
    api.add_resource(FinancialIndicatorListAPI, '/api/financial-indicators')
    api.add_resource(TaxListAPI, '/api/taxes')
    api.add_resource(ContactListAPI, '/api/contacts')
    api.add_resource(AddressListAPI, '/api/addresses')
    api.add_resource(OkvedListAPI, '/api/okveds')
    api.add_resource(IndustryListAPI, '/api/industries')
    api.add_resource(CompanySizeListAPI, '/api/company-sizes')
    api.add_resource(SupportListAPI, '/api/supports')
    api.add_resource(InvestmentExportListAPI, '/api/investment-exports')
    api.add_resource(PropertyLandListAPI, '/api/property-lands')
    api.add_resource(ProductionListAPI, '/api/productions')
    