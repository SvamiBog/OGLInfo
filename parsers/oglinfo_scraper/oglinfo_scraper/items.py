#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy


class AutoAdItem(scrapy.Item):
    # Идентификаторы и метаданные
    id_ad = scrapy.Field()              # Unique ID объявления
    createdAt = scrapy.Field()          # Дата создания (ISO строка)
    # Основная информация
    title = scrapy.Field()              # Заголовок объявления
    url_ad = scrapy.Field()             # Ссылка на объявление
    # Локация
    city = scrapy.Field()
    region = scrapy.Field()
    # Цена и валюта
    price = scrapy.Field()
    currencyCode = scrapy.Field()
    # Краткое описание и флаги продвижения
    short_description = scrapy.Field()
    is_highlighted = scrapy.Field()
    is_promoted = scrapy.Field()
    bump_date = scrapy.Field()
    # Параметры из advert.parameters
    make = scrapy.Field()
    model = scrapy.Field()
    version = scrapy.Field()
    year = scrapy.Field()
    fuel_type = scrapy.Field()
    gearbox = scrapy.Field()
    mileage = scrapy.Field()
    engine_capacity = scrapy.Field()
    color = scrapy.Field()
    transmission = scrapy.Field()
    engine_power = scrapy.Field()
    # Продавец
    sellerLink = scrapy.Field()

    # Флаги пайплайна
    new_ad = scrapy.Field()
    price_update = scrapy.Field()
    old_price = scrapy.Field()
    new_price = scrapy.Field()
    check_sold = scrapy.Field()
