from sqlalchemy import Integer, Column, String, Float

from health_care.database import BaseModle, session
from .mixins import CreationMixin


class User(CreationMixin, BaseModle):
    __tablename__ = 'bot_user'

    id = Column(Integer, primary_key=True)
    peer_id = Column(String)
    access_hash = Column(String)
    location_langitude = Column(Float)
    location_latitude = Column(Float)

    @classmethod
    def exists(cls, peer_id):
        return session.query(cls).filter(cls.peer_id == peer_id).one_or_none()
