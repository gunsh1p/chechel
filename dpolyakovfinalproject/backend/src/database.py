"""
Модуль инициализации базы данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Создает и предоставляет сессию базы данных, гарантируя её закрытие после завершения работы"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализирует базу данных, создавая все таблицы
    Также создает "базового" администратора, если его нет.
    Также создает одно изначальное место для брони"""
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована (таблицы созданы).")

    # Импортируем только внутри функции, чтобы избежать циклического импорта
    from src.models.user import User
    from src.auth import hash_password
    from src.models.place import Place
    db = SessionLocal()
    try:
        # Добавляем админа
        admin = db.query(User).filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                hashed_password=hash_password('admin123'),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Создан 'базовый' администратор: admin / admin123")
        else:
            print("Администратор уже существует.")

        # Добавляем место
        if db.query(Place).count() == 0:
            test_place = Place(
                name='F206',
                location='2 этаж ЦУ',
                description='То самое место, о котором ходят слухи',
                is_available=True
            )
            db.add(test_place)
            db.commit()
            print("Было создано место: F206")
    except Exception as e:
        print(f"Ошибка при создании администратора или тестового места: {e}")
        db.rollback()
    finally:
        db.close()


def reset_db():
    """Полностью сбрасывает схему базы данных и инициализирует её заново"""
    Base.metadata.drop_all(bind=engine)
    print("Схема базы данных удалена.")
    init_db()


if __name__ == "__main__":
    reset_db()
