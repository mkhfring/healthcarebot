import enum

from sqlalchemy import Integer, Column, Enum, String
from sqlalchemy.orm import relationship

from health_care.database import BaseModel


class CategoryEnum(enum.Enum):
    TEENAGER = 0
    ELDER = 1
    YOUTH = 2
    NEWBORN = 3
    KID = 4
    PREGNANT = 5
    MIDDLE_AGE = 6
    LACTATING = 7
    PRE_PARTUATION = 8


class Category(BaseModel):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    category_type = Column(Enum(CategoryEnum), unique=True)
    description = Column(String)
    services = relationship("Service")

