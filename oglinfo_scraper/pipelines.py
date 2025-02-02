from database.db_config import get_session
from database.models import AutoAd, AutoAdHistory
from datetime import datetime


class OtomotoScraperPipeline:
    def process_item(self, item, spider):
        if "price_update" in item and item["price_update"]:
            pass
        elif "new_ad" in item and item["new_ad"]:
            self.add_new_auto(item, spider)
        elif "check_sold" in item and item["check_sold"]:
            self.process_sold_ads(item, spider)

        return item


    def add_new_auto(self, item, spider):
        """Добавление нового объявления в базу данных и запись истории."""
        with get_session() as session:
            # Проверяем наличие объявления по data_id
            existing_ad = session.query(AutoAd).filter_by(data_id=item["data_id"]).first()
            if existing_ad:
                spider.logger.info(f"Объявление с data_id {item['data_id']} уже существует в базе, пропускаем вставку.")
                return

            try:
                new_ad = AutoAd(
                    title=item["title"],
                    price=item["price"],
                    currency=item["currency"],
                    location=item["location"],
                    country=item.get("country"),
                    url=item["url"],
                    data_id=item["data_id"],
                    created_at=item["created_at"],
                    brand=item["brand"],
                    model=item["model"],
                    year=item["year"],
                    mileage=item["mileage"],
                    fuel=item["fuel"],
                    transmission=item["transmission"],
                    drive=item["drive"],
                    engine_capacity=item["engine_capacity"],
                    power=item["power"],
                    body_type=item["body_type"],
                    doors=item["doors"],
                    color=item["color"],
                    description=item["description"],
                    dealer=item["dealer"],
                    condition=item["condition"],
                    platform=item["platform"],
                    sold_at=item.get("sold_at"),
                )
                session.add(new_ad)
                session.flush()  # Получаем ID нового объявления

                history_entry = AutoAdHistory(
                    auto_ad_id=new_ad.id,
                    price=new_ad.price,
                    currency=new_ad.currency,
                    status="new",
                    timestamp=datetime.utcnow(),
                )
                session.add(history_entry)
                session.commit()
            except Exception as e:
                session.rollback()
                spider.logger.error(f"Ошибка при добавлении нового объявления {item['url']} с data_id {item['data_id']}: {e}")


    def process_sold_ads(self, item, spider):
        """Помечает объявления, отсутствующие в списке обработанных, как проданные."""
        with get_session() as session:
            try:
                # Получаем все объявления из базы
                db_ads = session.query(AutoAd).all()
                for ad in db_ads:
                    if ad.data_id not in spider.processed_ids and ad.sold_at is None:
                        ad.sold_at = datetime.utcnow()
                        session.add(ad)
                        history = AutoAdHistory(
                            auto_ad_id=ad.id,
                            price=ad.price,
                            currency=ad.currency,
                            status="sold",
                            timestamp=datetime.utcnow(),
                        )
                        session.add(history)
                        spider.logger.info(f"Объявление с data_id {ad.data_id} помечено как проданное.")
                session.commit()
            except Exception as e:
                spider.logger.error(f"Ошибка при обработке проданных объявлений: {e}")


    def close_spider(self, spider):
        """Помечает объявления как проданные, если они отсутствуют в списке processed_ids."""
        with get_session() as session:
            try:
                db_data_ids = {ad.data_id for ad in session.query(AutoAd.data_id).all()}
                missing_ids = db_data_ids - spider.processed_ids
                for data_id in missing_ids:
                    ad = session.query(AutoAd).filter_by(data_id=data_id).first()
                    if ad and ad.sold_at is None:
                        ad.sold_at = datetime.utcnow()
                        session.add(ad)
                        history = AutoAdHistory(
                            auto_ad_id=ad.id,
                            price=ad.price,
                            currency=ad.currency,
                            status="sold",
                            timestamp=datetime.utcnow(),
                        )
                        session.add(history)
                        spider.logger.info(f"Объявление с data_id {data_id} помечено как проданное.")
                session.commit()
            except Exception as e:
                spider.logger.error(f"Ошибка обработки проданных объявлений: {e}")
