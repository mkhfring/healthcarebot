from sqlalchemy import Integer, Column, String, Float
from sqlalchemy.orm import relationship

from health_care.database import BaseModel, session
from .mixins import CreationMixin
from .location import Location


class User(CreationMixin, BaseModel):
    __tablename__ = 'bot_user'

    id = Column(Integer, primary_key=True)
    peer_id = Column(String)
    access_hash = Column(String)
    locations = relationship('Location')

    @classmethod
    def exists(cls, peer_id):
        return session.query(cls).filter(cls.peer_id == peer_id).one_or_none()
