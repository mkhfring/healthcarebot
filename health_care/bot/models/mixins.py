from sqlalchemy import Column, DateTime


class CreationMixin:
    created_at = Column(
        DateTime,
        nullable=False)
