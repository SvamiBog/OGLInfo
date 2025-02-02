from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class AutoAd(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Уникальный ID
    title: str  # Заголовок объявления
    price: Optional[int] = None  # Цена
    currency: Optional[str] = None  # Валюта (PLN, EUR и т.д.)
    location: Optional[str] = None  # Местоположение
    country: Optional[str] = None  # Страна продажи авто
    url: str = Field(unique=True, index=True)  # Уникальная ссылка
    data_id: str = Field(unique=True, index=True)  # Уникальный идентификатор объявления (data-id)
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Дата добавления объявления

    # Детали автомобиля
    brand: Optional[str] = None  # Марка
    model: Optional[str] = None  # Модель
    year: Optional[int] = None  # Год выпуска
    mileage: Optional[int] = None  # Пробег
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

    # Связь с историей изменений
    history: List["AutoAdHistory"] = Relationship(back_populates="auto_ad")


class AutoAdHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Уникальный ID
    auto_ad_id: int = Field(foreign_key="autoad.id")  # Внешний ключ на AutoAd
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # Дата и время изменения
    price: Optional[int] = None  # Цена
    currency: Optional[str] = None  # Валюта
    status: Optional[str] = None  # Статус (например, "active", "sold", "removed")

    # Связь с объявлением
    auto_ad: AutoAd = Relationship(back_populates="history")
