from sqlalchemy import Column, Integer, String, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class CompanySize(SqlAlchemyBase):
    __tablename__ = 'company_sizes'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    size_final = Column(String(100)) # Размер предприятия (итог)
    size_by_employees = Column(String(100))  # Размер предприятия (по численности)
    size_by_revenue = Column(String(100))  # Размер предприятия (по выручке)
