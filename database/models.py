from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class AutoAd(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Уникальный ID
    title: str  # Заголовок объявления
    price: Optional[float] = None  # Цена
    currency: Optional[str] = None  # Валюта (PLN, EUR и т.д.)
    location: Optional[str] = None  # Местоположение
    country: Optional[str] = None  # Страна продажи авто
    url: str = Field(unique=True, index=True)  # Уникальная ссылка
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Дата добавления объявления

    # Детали автомобиля
    brand: Optional[str] = None  # Марка
    model: Optional[str] = None  # Модель
    year: Optional[int] = None  # Год выпуска
    mileage: Optional[int] = None  # Пробег
    mileage_unit: Optional[str] = None  # Единица измерения пробега (км, миль)
    fuel: Optional[str] = None  # Тип топлива
    transmission: Optional[str] = None  # Трансмиссия
    drive: Optional[str] = None  # Привод
    engine_capacity: Optional[float] = None  # Объем двигателя (литры)
    power: Optional[int] = None  # Мощность (л.с.)
    body_type: Optional[str] = None  # Тип кузова
    doors: Optional[int] = None  # Количество дверей
    color: Optional[str] = None  # Цвет автомобиля

    # Дополнительные поля
    description: Optional[str] = None  # Описание
    dealer: Optional[str] = None  # Продавец (частник или дилер)
    condition: Optional[str] = None  # Состояние (новый, подержанный)
    platform: Optional[str] = None  # Ресурс размещения объявления (Otomoto, Mobile.de)
    sold_at: Optional[datetime] = None  # Дата продажи (или исчезновения объявления)
