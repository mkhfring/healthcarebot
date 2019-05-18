from datetime import datetime
from sqlalchemy import Column, DateTime


class CreationMixin:
    created_at = Column(
        DateTime,
        default=datetime.now(),
        nullable=False)
