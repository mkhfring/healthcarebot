import enum

from sqlalchemy import Integer, Column, Enum, String, ForeignKey

from health_care.database import BaseModel


class Service(BaseModel):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
