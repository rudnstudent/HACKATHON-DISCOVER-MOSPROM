from sqlalchemy import Column, Integer, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class InvestmentExport(SqlAlchemyBase):
    __tablename__ = 'investment_exports'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    moscow_investments = Column(Float)  # Инвестиции в Москву, тыс. руб.
    export_volume = Column(Float)  # Объем экспорта, тыс. руб.
