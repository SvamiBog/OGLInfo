from database.db_config import get_session
from database.models import AutoAd
import logging


class OtomotoScraperPipeline:
    def process_item(self, item, spider):
        """Сохранение объявления в базу данных"""
        with next(get_session()) as session:
            try:
                ad = AutoAd(
                    title=item.get('title'),
                    price=item.get('price'),
                    currency=item.get('currency'),
                    location=item.get('location'),
                    country=item.get('country'),
                    url=item.get('url'),
                    created_at=item.get('created_at'),

                    # Детали автомобиля
                    brand=item.get('brand'),
                    model=item.get('model'),
                    year=item.get('year'),
                    mileage=item.get('mileage'),
                    fuel=item.get('fuel'),
                    transmission=item.get('transmission'),
                    drive=item.get('drive'),
                    engine_capacity=item.get('engine_capacity'),
                    power=item.get('power'),
                    body_type=item.get('body_type'),
                    doors=item.get('doors'),
                    color=item.get('color'),

                    # Дополнительные поля
                    description=item.get('description'),
                    dealer=item.get('dealer'),
                    condition=item.get('condition'),
                    platform=item.get('platform'),
                    sold_at=item.get('sold_at')
                )
                session.add(ad)
                session.commit()
            except Exception as e:
                logging.error(f"Ошибка сохранения данных: {e}")
        return item
