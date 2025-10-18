from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class Address(SqlAlchemyBase):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    address_type = Column(String(50))  # 'Юридический', 'Производства' и тд
    full_address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    district = Column(String(100))
    area = Column(String(100))
