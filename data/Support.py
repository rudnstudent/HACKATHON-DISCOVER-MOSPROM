from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
import sqlalchemy
from .db_session import SqlAlchemyBase


class Support(SqlAlchemyBase):
    __tablename__ = 'supports'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    support_data = Column(Text)  # Данные о мерах поддержки
    special_status = Column(String(255))  # Наличие особого статуса
    platform_final = Column(String(100))  # Площадка итог
    moscow_support_received = Column(Boolean)  # Получена поддержка от г. Москвы
    system_forming_enterprise = Column(Boolean)  # Системообразующее предприятие
    sme_status = Column(String(100))  # Статус МСП
