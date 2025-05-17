# makes_models_scraper/makes_models_scraper/spiders/makes_models.py

import json
import scrapy
from makes_models_scraper.items import MakeModelItem

class MakesModelsSpider(scrapy.Spider):
    name = 'makes_models'
    allowed_domains = ['otomoto.pl']
    start_urls = ['https://www.otomoto.pl/osobowe/']

    def clean_raw_data(self, raw: str) -> str:
        """
        Убираем внешние кавычки и экранированные кавычки внутри строки.
        """
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        return raw.replace('\\"', '"')

    def extract_filters(self, urql_state: dict) -> dict | None:
        """
        Проходит по всем state в urqlState, очищает поле data и
        пытается распарсить JSON, возвращая advertSearchFilters.
        """
        for state in urql_state.values():
            print(f'=============>{state}<==================')
            raw = state.get('data', '{}')
            if isinstance(raw, str):
                raw = self.clean_raw_data(raw)
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if 'advertSearchFilters' in parsed:
                return parsed['advertSearchFilters']
        return None

    def parse(self, response):
        # 1) Получаем весь JSON из <script id="__NEXT_DATA__">
        script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data = json.loads(script)

        # 2) Ищем advertSearchFilters в urqlState
        urql = data['props']['pageProps']['urqlState']
        filters = self.extract_filters(urql)
        if not filters:
            self.logger.error("Не найден advertSearchFilters на главной странице")
            return

        # 3) Перебираем блок make — все бренды
        for state in filters['states']:
            if state['filterId'] == 'filter_enum_make':
                for group in state['values']:
                    for val in group['values']:
                        make_name = val['name']
                        make_slug = val['id']
                        yield scrapy.Request(
                            url=f'https://www.otomoto.pl/osobowe/{make_slug}/',
                            callback=self.parse_models,
                            meta={'make_name': make_name, 'make_slug': make_slug}
                        )
                break

    def parse_models(self, response):
        make_name = response.meta['make_name']
        make_slug = response.meta['make_slug']

        # 1) Читаем JSON из страницы марки
        script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data = json.loads(script)

        # 2) Извлекаем advertSearchFilters
        urql = data['props']['pageProps']['urqlState']
        filters = self.extract_filters(urql)
        if not filters:
            self.logger.debug(f"No advertSearchFilters for make {make_name!r} — skipping")
            return

        # 3) Перебираем блок model — все модели текущей марки
        for state in filters['states']:
            if state['filterId'] == 'filter_enum_model':
                for group in state['values']:
                    for val in group['values']:
                        yield MakeModelItem(
                            make_name=make_name,
                            make_slug=make_slug,
                            model_name=val['name'],
                            model_slug=val['id']
                        )
                break
