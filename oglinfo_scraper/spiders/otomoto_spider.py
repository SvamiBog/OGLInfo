import scrapy
import json
from database.db_config import get_session
from oglinfo_scraper.items import AutoAdItem
from database.models import AutoAd, AutoAdHistory
from datetime import datetime


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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_urls = set()
        # Будем хранить обработанные data_id, а не URL
        self.processed_ids = set()


    def parse(self, response):
        last_page = response.css("ul.pagination-list li:nth-last-child(4) a span::text").get()
        last_page = int(last_page) if last_page else 1
        self.logger.info(f"Найдено страниц пагинации: {last_page}")

        for page in range(1, last_page + 1):
            url = f"https://www.otomoto.pl/osobowe/uzywane/acura?search%5Border%5D=created_at_first%3Adesc&page={page}"
            self.logger.info(f"Генерация запроса для страницы: {url}")
            yield scrapy.Request(url=url, callback=self.parse_page)


    def parse_page(self, response):
        articles = response.css("article[data-id]")
        ads_data = response.css("script[type='application/ld+json']::text").get()

        if not ads_data:
            self.logger.error("JSON данные не найдены на странице")
            return

        try:
            ads_json = json.loads(ads_data).get("mainEntity", {}).get("itemListElement", [])
        except json.JSONDecodeError:
            self.logger.error("Ошибка декодирования JSON данных")
            return

        # Извлекаем URL и data-id из каждого объявления (article)
        urls = []
        data_ids = []
        for article in articles:
            url = response.urljoin(article.css("h2 a::attr(href)").get())
            data_id = article.attrib.get("data-id")
            urls.append(url)
            data_ids.append(data_id)

        # Предполагаем, что порядок в ads_json соответствует порядку статей
        for ad_json, url, data_id in zip(ads_json, urls, data_ids):
            item = AutoAdItem()
            item["price"] = ad_json["priceSpecification"]["price"]
            item["url"] = url
            item["data_id"] = data_id
            yield from self.check_ad_in_database(response, item)


    def check_ad_in_database(self, response, item):
        with get_session() as session:
            data_id = item["data_id"]
            existing_ad = session.query(AutoAd).filter_by(data_id=data_id).first()
            self.processed_ids.add(data_id)

            if existing_ad:
                # Если объявление найдено по data_id, проверяем статус sold_at и цену.
                if existing_ad.sold_at is not None:
                    current_price = int(existing_ad.price) if existing_ad.price else 0
                    new_price = int(item["price"])
                    if current_price != new_price:
                        old_price = existing_ad.price
                        existing_ad.price = item["price"]
                        item["price_update"] = True
                        item["old_price"] = old_price
                        item["new_price"] = existing_ad.price
                        self.logger.info(
                            f"Обновление цены и восстановление объявления: data_id {data_id}, старая цена: {old_price}, новая цена: {new_price}"
                        )
                    else:
                        self.logger.info(
                            f"Объявление data_id {data_id} найдено, ранее помечено как проданное, но цена не изменилась. Снимаем отметку 'продано'."
                        )
                    # Снимаем отметку о продаже и обновляем URL, если он изменился.
                    existing_ad.sold_at = None
                    if existing_ad.url != item["url"]:
                        existing_ad.url = item["url"]
                    session.add(existing_ad)
                    session.commit()
                    yield item
                else:
                    current_price = int(existing_ad.price) if existing_ad.price else 0
                    new_price = int(item["price"])
                    if current_price != new_price:
                        old_price = existing_ad.price
                        existing_ad.price = item["price"]
                        session.add(existing_ad)
                        item["price_update"] = True
                        item["old_price"] = old_price
                        item["new_price"] = existing_ad.price
                        self.logger.info(
                            f"Обновление цены: data_id {data_id}, старая цена: {old_price}, новая цена: {new_price}"
                        )
                        session.commit()
                        yield item
            else:
                # Объявление не найдено – передаем на полный парсинг.
                self.new_urls.add(item["url"])
                yield scrapy.Request(
                    url=item["url"],
                    callback=self.parse_ad,
                    meta={"item_url": item["url"], "data_id": data_id}
                )
            session.commit()


    def parse_ad(self, response):
        """Парсинг полного объявления."""
        script_data = response.css("script#__NEXT_DATA__::text").get()
        if not script_data:
            self.logger.error(f"Нет данных JSON в объявлении: {response.url}")
            return

        try:
            data = json.loads(script_data)
            advert = data.get("props", {}).get("pageProps", {}).get("advert", {})
        except json.JSONDecodeError:
            self.logger.error(f"Ошибка декодирования JSON в объявлении: {response.url}")
            return

        if not advert:
            self.logger.error(f"Данные объявления отсутствуют в JSON: {response.url}")
            return

        # Обработка даты создания объявления
        created_at_raw = response.css("p.e1jwj3576::text").get()
        created_at = None
        if created_at_raw:
            try:
                created_at_parts = created_at_raw.split()
                if len(created_at_parts) == 4:
                    day, month_polish, year, time = created_at_parts
                    month = self.POLISH_MONTHS.get(month_polish.lower())
                    if month:
                        created_at_str = f"{year}-{month}-{day} {time}"
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M")
            except Exception:
                self.logger.error(f"Ошибка обработки даты создания объявления: {created_at_raw}")

        title = advert.get("title")
        price = advert.get("price", {}).get("value")
        currency = advert.get("price", {}).get("currency")
        location = advert.get("seller", {}).get("location", {}).get("address")
        country = advert.get("seller", {}).get("location", {}).get("country", "Polska")
        details = {detail.get("key"): detail.get("value") for detail in advert.get("details", [])}

        mileage_raw = details.get("mileage", "")
        mileage = None
        if mileage_raw:
            try:
                mileage = int(mileage_raw.replace(" ", "").replace("km", "").strip())
            except ValueError:
                self.logger.warning(f"Ошибка обработки пробега: {mileage_raw}")

        engine_capacity_raw = details.get("engine_capacity", "")
        engine_capacity = None
        if engine_capacity_raw:
            try:
                engine_capacity = int(engine_capacity_raw.replace(" ", "").replace("cm3", "").strip())
            except ValueError:
                self.logger.warning(f"Ошибка обработки объёма двигателя: {engine_capacity_raw}")

        power_raw = details.get("engine_power")
        power = None
        if power_raw:
            try:
                power = int(power_raw.replace("KM", "").strip())
            except ValueError:
                self.logger.warning(f"Ошибка обработки мощности двигателя: {power_raw}")

        item = AutoAdItem()
        item["new_ad"] = True
        item["url"] = response.url
        item["data_id"] = response.meta.get("data_id")  # Передаём data_id из meta
        item["title"] = title
        item["price"] = float(price) if price else None
        item["currency"] = currency
        item["location"] = location
        item["country"] = country
        item["brand"] = details.get("make")
        item["model"] = details.get("model")
        item["year"] = int(details.get("year")) if details.get("year") and details.get("year").isdigit() else None
        item["mileage"] = mileage
        item["fuel"] = details.get("fuel_type")
        item["transmission"] = details.get("gearbox")
        item["drive"] = details.get("transmission")
        item["engine_capacity"] = engine_capacity
        item["power"] = power
        item["body_type"] = details.get("body_type")
        item["doors"] = int(details.get("nr_seats")) if details.get("nr_seats") and details.get("nr_seats").isdigit() else None
        item["color"] = details.get("color")
        item["description"] = advert.get("description")
        item["dealer"] = advert.get("seller", {}).get("name")
        item["condition"] = details.get("new_used")
        item["platform"] = "Otomoto"
        item["created_at"] = created_at
        item["sold_at"] = None

        yield item
