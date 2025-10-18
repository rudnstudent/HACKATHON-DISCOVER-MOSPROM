from sqlalchemy import Column, Integer, String, Float, ForeignKey
import sqlalchemy
from .db_session import SqlAlchemyBase

class FinancialIndicator(SqlAlchemyBase):
    __tablename__ = 'financial_indicators'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    year = Column(Integer, nullable=False)
    revenue = Column(Float)  # Выручка предприятия, тыс. руб.
    net_profit = Column(Float)  # Чистая прибыль (убыток), тыс. руб.
    employee_count = Column(Integer)  # Среднесписочная численность персонала (всего по компании)
    employee_count_moscow = Column(Integer)  # Среднесписочная численность персонала, работающего в Москве
    payroll_all_employees = Column(Float)  # Фонд оплаты труда всех сотрудников организации, тыс. руб
    payroll_moscow_employees = Column(Float)  # Фонд оплаты труда сотрудников, работающих в Москве, тыс. руб
    avg_salary_all_employees = Column(Float)  # Средняя з.п. всех сотрудников организации, тыс.руб.
    avg_salary_moscow_employees = Column(Float)  # Средняя з.п. сотрудников, работающих в Москве, тыс.руб.