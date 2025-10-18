from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Boolean
import sqlalchemy
from .db_session import SqlAlchemyBase


class Production(SqlAlchemyBase):
    __tablename__ = 'productions'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    manufactured_products = Column(Text)  # Производимая продукция
    standardized_products = Column(Text)  # Стандартизированная продукция
    product_names = Column(Text)  # Название (виды производимой продукции)
    okpd2_products = Column(Text)  # Перечень производимой продукции по кодам ОКПД 2
    product_types_segments = Column(Text)  # Перечень производимой продукции по типам и сегментам
    product_catalog = Column(Text)  # Каталог продукции
    government_order = Column(Boolean)  # Наличие госзаказа
    production_capacity_utilization = Column(String(100))  # Уровень загрузки производственных мощностей
    export_supplies = Column(Boolean)  # Наличие поставок продукции на экспорт
    export_volume_previous_year = Column(Float)  # Объем экспорта (млн.руб.) за предыдущий календарный год
    export_countries = Column(Text)  # Перечень государств куда экспортируется продукция
    tn_ved_code = Column(String(50))  # Код ТН ВЭД ЕАЭС
