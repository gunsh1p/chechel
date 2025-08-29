"""
Модуль определения модели пользователя (User)
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.models.base import Base


class User(Base):
    """
    Определение модели пользователя
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    # Связываем таблицы User и Booking
    bookings = relationship("Booking", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
