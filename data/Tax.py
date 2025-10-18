from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase


class Tax(SqlAlchemyBase):
    __tablename__ = 'taxes'

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    moscow_taxes = Column(Float)  # Налоги, уплаченные в бюджет Москвы (без акцизов), тыс.руб.
    profit_tax = Column(Float)  # Налог на прибыль, тыс.руб.
    property_tax = Column(Float)  # Налог на имущество, тыс.руб.
    land_tax = Column(Float)  # Налог на землю, тыс.руб.
    personal_income_tax = Column(Float)  # НДФЛ, тыс.руб.
    transport_tax = Column(Float)  # Транспортный налог, тыс.руб.
    other_taxes = Column(Float)  # Прочие налоги
    excise_taxes = Column(Float)  # Акцизы, тыс. руб.