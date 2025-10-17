from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase

class FinancialIndicator(SqlAlchemyBase):
    __tablename__ = 'financial_indicators'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Float)
    net_profit = Column(Float)
    employee_count = Column(Integer)
    # ... и другие финансовые поля