from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager
import os

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем URL базы данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем, что переменная определена
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

# Создаём подключение к базе данных
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Функция для получения сессии
@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
