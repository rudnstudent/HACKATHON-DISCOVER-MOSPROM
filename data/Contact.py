from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class Contact(SqlAlchemyBase):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    contact_type = Column(String(100)) # 'Руководства', 'Сотрудника'
    name = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
