import scrapy
import json
import re
from datetime import datetime
from database.db_config import get_session
from database.models import AutoAd


class OtomotoSpider(scrapy.Spider):
    name = "otomoto"
    allowed_domains = ["otomoto.pl"]
    start_urls = [
        "https://www.otomoto.pl/osobowe/uzywane/acura?search%5Border%5D=created_at_first%3Adesc"
    ]

    # Словарь для перевода месяцев с польского
    POLISH_MONTHS = {
        "stycznia": "01",
        "lutego": "02",
        "marca": "03",
        "kwietnia": "04",
        "maja": "05",
        "czerwca": "06",
        "lipca": "07",
        "sierpnia": "08",
        "września": "09",
        "października": "10",
        "listopada": "11",
        "grudnia": "12",
    }

    def parse(self, response):
        # Получаем общее количество страниц из блока пагинации
        last_page = response.css("ul.pagination-list li:nth-last-child(4) a span::text").get()
        last_page = int(last_page) if last_page else 1

        self.logger.info(f"Найдено страниц пагинации: {last_page}")

        # Генерируем запросы для всех страниц
        for page in range(1, last_page + 1):
            url = f"https://www.otomoto.pl/osobowe/uzywane/acura?search%5Border%5D=created_at_first%3Adesc&page={page}"
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        # Получаем ссылки на объявления
        ads = response.css("article[data-id] h2 a::attr(href)").getall()

        with next(get_session()) as session:
            # Получаем ссылки из базы данных
            db_ads = {row.url: row.price for row in session.query(AutoAd.url, AutoAd.price).all()}

        # Новые объявления
        new_ads = [ad for ad in ads if ad not in db_ads]

        # Обновление цен для существующих объявлений
        for ad_url in ads:
            if ad_url in db_ads:
                response_price = response.css(f"article[data-id] a[href='{ad_url}'] span.offer-price__number::text").get()
                if response_price:
                    response_price = response_price.strip().replace(" ", "").replace("PLN", "")
                    if db_ads[ad_url] != response_price:
                        session.query(AutoAd).filter(AutoAd.url == ad_url).update({"price": response_price})
                        self.logger.info(f"Цена объявления {ad_url} обновлена: {response_price}")
                        session.commit()

        if not new_ads:
            self.logger.info("Новых объявлений нет.")
        else:
            self.logger.info(f"Найдены новые объявления: {len(new_ads)}")

        # Переходим к парсингу новых объявлений
        for ad_url in new_ads:
            yield scrapy.Request(url=ad_url, callback=self.parse_ad)


    def parse_ad(self, response):
        # Получаем данные из скрипта
        script_data = response.css("script#__NEXT_DATA__::text").get()
        if not script_data:
            self.logger.error("Нет данных в скрипте __NEXT_DATA__.")
            return

        data = json.loads(script_data)
        advert = data.get("props", {}).get("pageProps", {}).get("advert", {})

        if not advert:
            self.logger.error("Нет данных объявления в данных JSON.")
            return

        # Извлекаем дату создания объявления
        created_at_raw = response.css("p.e1jwj3576::text").get()
        if created_at_raw:
            created_at_parts = created_at_raw.split()
            if len(created_at_parts) == 4:
                day, month_polish, year, time = created_at_parts
                month = self.POLISH_MONTHS.get(month_polish.lower())
                if month:
                    created_at_str = f"{year}-{month}-{day} {time}"
                    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M")
                else:
                    created_at = None
            else:
                created_at = None
        else:
            created_at = None

        # Извлекаем данные
        title = advert.get("title")
        price = float(advert.get("price", {}).get("value", 0))
        currency = advert.get("price", {}).get("currency")
        location = advert.get("seller", {}).get("location", {}).get("address")
        country = advert.get("seller", {}).get("location", {}).get("country")

        # details хранится как список, преобразуем в словарь
        details = {detail.get("key"): detail.get("value") for detail in advert.get("details", [])}

        # Обработка числовых данных
        mileage_raw = details.get("mileage", "")
        mileage_match = re.search(r"(\d+)", mileage_raw.replace(" ", ""))
        mileage = int(mileage_match.group(1)) if mileage_match else None
        mileage_unit = "km" if "km" in mileage_raw else None

        engine_capacity_raw = details.get("engine_capacity", "")
        engine_capacity_match = re.search(r"([\d.]+)", engine_capacity_raw)
        engine_capacity = float(engine_capacity_match.group(1)) if engine_capacity_match else None

        power_raw = details.get("engine_power")
        power_match = re.search(r"(\d+)", power_raw)
        power = int(power_match.group(1)) if power_match else None


        # Сбор данных
        yield {
            "title": title,
            "price": price,
            "currency": currency,
            "location": location,
            "country": country,
            "url": response.url,
            "brand": details.get("make"),
            "model": details.get("model"),
            "year": int(details.get("year")) if details.get("year") and details.get("year").isdigit() else None,
            "mileage": mileage,
            "mileage_unit": mileage_unit,
            "fuel": details.get("fuel_type"),
            "transmission": details.get("gearbox"),
            "drive": details.get("transmission"),
            "engine_capacity": engine_capacity,
            "power": power,
            "body_type": details.get("body_type"),
            "doors": details.get("nr_seats"),
            "color": details.get("color"),
            "description": advert.get("description"),
            "dealer": advert.get("seller", {}).get("name"),
            "condition": details.get("new_used"),
            "platform": "Otomoto",
            "created_at": created_at,
            "sold_at": None,
        }
