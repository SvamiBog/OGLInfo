import scrapy

class AutoAdItem(scrapy.Item):
    # Основные поля объявления
    title = scrapy.Field()       # Заголовок объявления
    price = scrapy.Field()       # Цена
    currency = scrapy.Field()    # Валюта
    location = scrapy.Field()    # Местоположение
    country = scrapy.Field()     # Страна продажи авто
    url = scrapy.Field()         # Уникальная ссылка
    data_id = scrapy.Field()     # Уникальный идентификатор объявления (data-id)
    created_at = scrapy.Field()  # Дата добавления объявления

    # Детали автомобиля
    brand = scrapy.Field()       # Марка
    model = scrapy.Field()       # Модель
    year = scrapy.Field()        # Год выпуска
    mileage = scrapy.Field()     # Пробег
    fuel = scrapy.Field()        # Тип топлива
    transmission = scrapy.Field()  # Трансмиссия
    drive = scrapy.Field()         # Привод
    engine_capacity = scrapy.Field()  # Объем двигателя (литры)
    power = scrapy.Field()           # Мощность (л.с.)
    body_type = scrapy.Field()       # Тип кузова
    doors = scrapy.Field()           # Количество дверей
    color = scrapy.Field()           # Цвет автомобиля

    # Дополнительные поля
    description = scrapy.Field()     # Описание
    dealer = scrapy.Field()          # Продавец (частник или дилер)
    condition = scrapy.Field()       # Состояние (новый, подержанный)
    platform = scrapy.Field()        # Ресурс размещения объявления (Otomoto, Mobile.de)
    sold_at = scrapy.Field()         # Дата продажи (или исчезновения объявления)
    new_ad = scrapy.Field()
    price_update = scrapy.Field()
    old_price = scrapy.Field()
    new_price = scrapy.Field()
