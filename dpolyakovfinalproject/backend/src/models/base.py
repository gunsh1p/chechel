"""
Модуль с инициализацией базового класса для декларативного создания моделей SQLAlchemy
Таким образом спасаемся от возможных проблем с циклическим импортом
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
