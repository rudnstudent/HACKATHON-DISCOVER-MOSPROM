from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class Tax(SqlAlchemyBase):
    __tablename__ = 'taxes'

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    profit_tax = Column(Float)
    property_tax = Column(Float)
    land_tax = Column(Float)
    personal_income_tax = Column(Float)
    transport_tax = Column(Float)
    # ... и другие налоговые поляf