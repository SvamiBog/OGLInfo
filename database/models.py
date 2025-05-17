from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class CarMake(SQLModel, table=True):
    __tablename__ = "car_make"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(index=True, unique=True)

    models: List["CarModel"] = Relationship(back_populates="make")


class CarModel(SQLModel, table=True):
    __tablename__ = "car_model"

    id: Optional[int] = Field(default=None, primary_key=True)
    make_id: int = Field(foreign_key="car_make.id", index=True)
    name: str
    slug: str = Field(index=True, unique=True)

    make: Optional[CarMake] = Relationship(back_populates="models")
    ads: List["AutoAd"] = Relationship(back_populates="car_model")


class AutoAd(SQLModel, table=True):
    __tablename__ = "auto_ad"

    id_ad: str = Field(primary_key=True, index=True)
    createdAt: datetime
    make: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None
    url_ad: Optional[str] = Field(default=None, index=True)
    city: Optional[str] = None
    region: Optional[str] = None
    price: Optional[int] = None
    currencyCode: Optional[str] = None
    fuel_type: Optional[str] = None
    gearbox: Optional[str] = None
    mileage: Optional[int] = None
    engine_capacity: Optional[int] = None
    color: Optional[str] = None
    transmission: Optional[str] = None
    engine_power: Optional[int] = None
    sellerLink: Optional[str] = None
    sold_at: Optional[datetime] = None

    car_model_id: Optional[int] = Field(foreign_key="car_model.id", index=True)
    car_model: Optional[CarModel] = Relationship(back_populates="ads")

    history: List["AutoAdHistory"] = Relationship(
        back_populates="auto_ad",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AutoAdHistory(SQLModel, table=True):
    __tablename__ = "auto_ad_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    auto_ad_id: str = Field(foreign_key="auto_ad.id_ad", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price: Optional[int] = None
    currencyCode: Optional[str] = None
    status: Optional[str] = None

    auto_ad: Optional[AutoAd] = Relationship(back_populates="history")
