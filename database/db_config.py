from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
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

# Функция для получения сессии
def get_session():
    with Session(engine) as session:
        yield session
