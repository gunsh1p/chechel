"""
Модуль определения модели бронирования (Booking)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from src.models.base import Base


class Booking(Base):
    """
    Определение модели бронирования рабочего места
    """
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    place_id = Column(Integer, ForeignKey('places.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default='active', nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return (f"<Booking(id={self.id}, user_id={self.user_id}, place_id={self.place_id}, "
                f"start={self.start_time}, end={self.end_time}, status={self.status})>")
