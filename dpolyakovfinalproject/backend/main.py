"""
Запуск backend сервера
"""
from src import create_app
from src.database import init_db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("Пытаемся инициализировать базу данных...")
        try:
            init_db()
            print("Инициализация базы данных была закончена.")
        except Exception as e:
            print(f"Ошибка во время инициализации базы данных: {e}")
    app.run(host='0.0.0.0', port=5000, debug=True)
