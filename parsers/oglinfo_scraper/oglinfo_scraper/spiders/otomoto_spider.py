#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import math
import scrapy
import urllib.parse as up
from collections import OrderedDict
from oglinfo_scraper.items import AutoAdItem


class OtomotoSpider(scrapy.Spider):
    name = "otomoto"
    allowed_domains = ["otomoto.pl"]

    # ——— Константы ———
    BASE_URL        = "https://www.otomoto.pl/graphql"
    OPERATION_NAME  = "listingScreen"
    ITEMS_PER_PAGE  = 50

    # extensions с persistedQuery
    EXTENSIONS = OrderedDict([
        ("persistedQuery", OrderedDict([
            ("sha256Hash", "1a840f0ab7fbe2543d0d6921f6c963de8341e04a4548fd1733b4a771392f900a"),
            ("version",     1),
        ]))
    ])

    # неизменные части запроса
    BASE_FILTERS = [
        {"name": "filter_enum_make", "value": "audi"},
        {"name": "filter_enum_model", "value": "a6"},
        {"name": "filter_enum_generation", "value": "gen-c6-2004-2011"},
        {"name": "category_id", "value": "29"},
        {"name": "new_used",    "value": "used"},
    ]
    BASE_PARAMS = [
        "make","vin","offer_type","show_pir","fuel_type","gearbox",
        "country_origin","mileage","engine_capacity","color","engine_code",
        "transmission","engine_power","first_registration_year",
        "model","version","year"
    ]

    def start_requests(self):
        # Первый запрос — page=1, чтобы узнать общее число объявлений
        yield scrapy.Request(
            url=self.build_url(page=1),
            callback=self.parse_initial
        )

    def build_url(self, page: int) -> str:
        # OrderedDict задаёт точный порядок полей
        variables = OrderedDict([
            ("filters",               self.BASE_FILTERS),
            ("includeCepik",          False),
            ("includeFiltersCounters",False),
            ("includeNewPromotedAds", False),
            ("includePriceEvaluation",False),
            ("includePromotedAds",     False),
            ("includeRatings",        False),
            ("includeSortOptions",    False),
            ("includeSuggestedFilters",False),
            ("itemsPerPage",          self.ITEMS_PER_PAGE),
            ("maxAge",                60),
            ("page",                  page),
            ("parameters",            self.BASE_PARAMS),
            ("promotedInput",         {})
        ])

        # Компактный JSON без пробелов
        vars_compact = json.dumps(variables, separators=(',',':'))
        ext_compact  = json.dumps(self.EXTENSIONS, separators=(',',':'))

        return (
            f"{self.BASE_URL}"
            f"?operationName={self.OPERATION_NAME}"
            f"&variables={up.quote(vars_compact, safe='')}"
            f"&extensions={up.quote(ext_compact,  safe='')}"
        )

    def parse_initial(self, response):
        data = json.loads(response.text)
        # Берём общее число объявлений из listingScreen
        total_ads = data['data']['advertSearch']['totalCount']
        total_pages = math.ceil(total_ads / self.ITEMS_PER_PAGE)
        self.logger.info(f"Всего объявлений: {total_ads}, страниц: {total_pages}")

        response.meta['page'] = 1
        yield from self.parse_page(response)

        for page in range(2, total_pages + 1):
            yield scrapy.Request(
                url=self.build_url(page=page),
                callback = self.parse_page,
                meta = {'page': page},
                )


    def parse_page(self, response):
        data = json.loads(response.text)
        edges = data['data']['advertSearch']['edges']
        page = response.meta.get('page')
        self.logger.info(f"Парсим страницу {page}, найдено {len(edges)} объявлений")

        for edge in edges:
            vas = edge.get('vas', {})  # значение VAS-блока
            node = edge.get('node', {})  # основное объявление

            # --- 1) Вытащим параметры в простой словарь ---
            raw_params = node.get('parameters') or []
            params = {}
            for p in raw_params:
                key = p.get('key')
                val = p.get('value')
                if key and val is not None:
                    params[key] = val

            # --- 2) Цена: units → int, currencyCode → str ---
            amount = (node.get('price') or {}).get('amount') or {}
            price_units = amount.get('units')
            # при желании можно собирать и nanos: total = units + nanos/1e9
            currency = amount.get('currencyCode')

            item = AutoAdItem(
                id_ad=node.get('id'),
                createdAt=node.get('createdAt'),
                title=node.get('title'),
                url_ad=node.get('url'),
                city=(node.get('location') or {}).get('city', {}).get('name'),
                region=(node.get('location') or {}).get('region', {}).get('name'),
                price=price_units,
                currencyCode=currency,
                # если нужно, сохраняем короткое описание
                short_description=node.get('shortDescription'),

                # флаги продвижения (опционально)
                is_highlighted=vas.get('isHighlighted'),
                is_promoted=vas.get('isPromoted'),
                bump_date=vas.get('bumpDate'),

                # из params
                make=params.get('make'),
                model=params.get('model'),
                version=params.get('version'),
                year=params.get('year'),
                fuel_type=params.get('fuel_type'),
                gearbox=params.get('gearbox'),
                mileage=params.get('mileage'),
                engine_capacity=params.get('engine_capacity'),
                color=params.get('color'),
                transmission=params.get('transmission'),
                engine_power=params.get('engine_power'),

                sellerLink=(node.get('sellerLink') or {}).get('id'),
            )

            yield item
