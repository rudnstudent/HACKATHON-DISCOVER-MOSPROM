from sqlalchemy import Column, Integer, String, Text, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class Industry(SqlAlchemyBase):
    __tablename__ = 'industries'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    main_industry = Column(String(255))  # Основная отрасль
    main_subindustry = Column(String(255))  # Подотрасль (Основная)
    additional_industry = Column(String(255))  # Дополнительная отрасль
    additional_subindustry = Column(String(255))  # Подотрасль (Дополнительная)
    industry_presentations = Column(Text)  # Отраслевые презентации
    industry_by_spark = Column(String(255))  # Отрасль промышленности по Спарк и Справочнику
