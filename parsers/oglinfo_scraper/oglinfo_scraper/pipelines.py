#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from dateutil import parser
from sqlmodel import select
from database.db_config import get_session
from database.models import AutoAd, AutoAdHistory


class OtomotoPipeline:
    """
    - Добавляет новые объявления
    - Восстанавливает активность проданных
    - Обновляет цену и другие поля
    - По закрытию спайдера помечает как проданные отсутствующие
    """
    def __init__(self):
        self.processed_ids = set()
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        self.processed_ids.clear()
        self.logger.info("OtomotoPipeline: старт обработки.")

    def process_item(self, item, spider):
        ad_id = item.get("id_ad")
        self.processed_ids.add(ad_id)
        # Конвертация даты из ISO строки в datetime
        created_at = None
        if item.get("createdAt"):
            created_at = parser.isoparse(item["createdAt"])

        with get_session() as session:
            ad = session.get(AutoAd, ad_id)
            if ad:
                # восстановление активности, если было продано
                if ad.sold_at:
                    ad.sold_at = None
                    session.add(AutoAdHistory(
                        auto_ad_id=ad.id_ad,
                        price=item.get("price"),
                        currencyCode=item.get("currencyCode"),
                        status="reappeared",
                        timestamp=datetime.utcnow()
                    ))
                # проверка и обновление цены
                new_price = item.get("price")
                if new_price is not None and ad.price != new_price:
                    old = ad.price
                    ad.price = new_price
                    session.add(AutoAdHistory(
                        auto_ad_id=ad.id_ad,
                        price=new_price,
                        currencyCode=item.get("currencyCode"),
                        status="updated",
                        timestamp=datetime.utcnow()
                    ))
                # обновляем остальные поля
                ad.title = item.get("title", ad.title)
                ad.url_ad = item.get("url_ad", ad.url_ad)
                ad.city = item.get("city", ad.city)
                ad.region = item.get("region", ad.region)
                ad.color = item.get("color", ad.color)
                session.add(ad)
            else:
                # создаём новое объявление
                ad = AutoAd(
                    id_ad=ad_id,
                    createdAt=created_at,
                    make=item.get("make"),
                    model=item.get("model"),
                    version=item.get("version"),
                    year=int(item.get("year")) if item.get("year") and str(item.get("year")).isdigit() else None,
                    title=item.get("title"),
                    url_ad=item.get("url_ad"),
                    city=item.get("city"),
                    region=item.get("region"),
                    price=item.get("price"),
                    currencyCode=item.get("currencyCode"),
                    fuel_type=item.get("fuel_type"),
                    gearbox=item.get("gearbox"),
                    mileage=int(item.get("mileage")) if item.get("mileage") and str(item.get("mileage")).isdigit() else None,
                    engine_capacity=int(item.get("engine_capacity")) if item.get("engine_capacity") and str(item.get("engine_capacity")).isdigit() else None,
                    color=item.get("color"),
                    transmission=item.get("transmission"),
                    engine_power=int(item.get("engine_power")) if item.get("engine_power") and str(item.get("engine_power")).isdigit() else None,
                    sellerLink=item.get("sellerLink")
                )
                session.add(ad)
                session.add(AutoAdHistory(
                    auto_ad_id=ad.id_ad,
                    price=ad.price,
                    currencyCode=ad.currencyCode,
                    status="new",
                    timestamp=datetime.utcnow()
                ))
            session.commit()
        return item

    def close_spider(self, spider):
        cutoff = datetime.utcnow()
        with get_session() as session:
            stmt = select(AutoAd).where(AutoAd.sold_at.is_(None))
            result = session.execute(stmt)
            for ad in result.scalars().all():
                if ad.id_ad not in self.processed_ids:
                    ad.sold_at = cutoff
                    session.add(AutoAdHistory(
                        auto_ad_id=ad.id_ad,
                        price=ad.price,
                        currencyCode=ad.currencyCode,
                        status="sold",
                        timestamp=cutoff
                    ))
                    session.add(ad)
                    self.logger.info(f"Объявление {ad.id_ad} помечено проданным.")
            session.commit()
        self.logger.info("OtomotoPipeline: завершение обработки.")
