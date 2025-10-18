from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text
import sqlalchemy
from .db_session import SqlAlchemyBase


class Organization(SqlAlchemyBase):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inn = Column(String(12), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500))
    spark_status = Column(String(100))
    internal_status = Column(String(100))
    final_status = Column(String(100))
    registry_addition_date = Column(String(50))
    registration_date = Column(String(50))
    manager_name = Column(String(255))
    website = Column(String(255))
    email = Column(String(255))
    general_info = Column(Text)
    head_organization = Column(String(255))  # Головная организация
    head_organization_inn = Column(String(12))  # ИНН головной организации
    head_organization_relation_type = Column(String(100))  # Вид отношения головной организации
    
    # Связи с другими таблицами
    addresses = sqlalchemy.orm.relationship('Address', backref='organization', lazy=True)
    financial_indicators = sqlalchemy.orm.relationship('FinancialIndicator', backref='organization', lazy=True)
    contacts = sqlalchemy.orm.relationship('Contact', backref='organization', lazy=True)
    taxes = sqlalchemy.orm.relationship('Tax', backref='organization', lazy=True)
    okveds = sqlalchemy.orm.relationship('Okved', backref='organization', lazy=True)
    industries = sqlalchemy.orm.relationship('Industry', backref='organization', lazy=True)
    company_sizes = sqlalchemy.orm.relationship('CompanySize', backref='organization', lazy=True)
    supports = sqlalchemy.orm.relationship('Support', backref='organization', lazy=True)
    investment_exports = sqlalchemy.orm.relationship('InvestmentExport', backref='organization', lazy=True)
    property_lands = sqlalchemy.orm.relationship('PropertyLand', backref='organization', lazy=True)
    productions = sqlalchemy.orm.relationship('Production', backref='organization', lazy=True)