from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
import sqlalchemy
from .db_session import SqlAlchemyBase

class Okved(SqlAlchemyBase):
    __tablename__ = 'okveds'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    okved_type = Column(String(100)) # 'Основной', 'Производственный'
    code = Column(String(20))
    description = Column(Text)