from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class PropertyLand(SqlAlchemyBase):
    __tablename__ = 'property_lands'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    # Земельный участок
    land_cadastral_number = Column(String(50))  # Кадастровый номер ЗУ
    land_area = Column(Float)  # Площадь ЗУ
    land_use_type = Column(String(255))  # Вид разрешенного использования ЗУ
    land_ownership_type = Column(String(100))  # Вид собственности ЗУ
    land_owner = Column(String(255))  # Собственник ЗУ
    # Объекты капитального строительства
    building_cadastral_number = Column(String(50))  # Кадастровый номер ОКСа
    building_area = Column(Float)  # Площадь ОКСов
    building_use_type = Column(String(255))  # Вид разрешенного использования ОКСов
    building_type_purpose = Column(String(255))  # Тип строения и цель использования
    building_ownership_type = Column(String(100))  # Вид собственности ОКСов
    building_owner = Column(String(255))  # СобственникОКСов
    production_area = Column(Float)  # Площадь производственных помещений, кв.м.
