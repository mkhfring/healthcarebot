from sqlalchemy import Integer, Column, String, Float, ForeignKey

from health_care.database import BaseModel, session
from .mixins import CreationMixin


class Location(BaseModel):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    langitude = Column(Float)
    latitude = Column(Float)
    user_id = Column(Integer, ForeignKey('bot_user.id'))
