"""
Модуль определения модели места (Place)
"""
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from src.models.base import Base


class Place(Base):
    """
    Определение модели рабочего места/помещения
    """
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)

    # Связываем таблицы Place и Booking
    bookings = relationship("Booking", backref="place", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Place(id={self.id}, name='{self.name}', location='{self.location}')>"
