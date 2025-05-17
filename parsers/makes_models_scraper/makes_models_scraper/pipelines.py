# makes_models_scraper/makes_models_scraper/pipelines.py

import re
import unidecode
from sqlalchemy.exc import IntegrityError

from database.db_config import get_session
from database.models import CarMake, CarModel
from makes_models_scraper.items import MakeModelItem


def slugify_text(text: str) -> str:
    """
    Простой slugifier:
     1) unidecode — убираем диакритику,
     2) lower()  — к нижнему регистру,
     3) re.sub   — любые не a–z0–9 → дефис,
     4) strip    — обрезаем лишние дефисы.
    """
    text = unidecode.unidecode(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


class MakeModelPipeline:
    def process_item(self, item, spider):
        # Мы обрабатываем только элементы MakeModelItem
        if not isinstance(item, MakeModelItem):
            return item

        # Сгенерировать слаги
        make_slug  = slugify_text(item['make_name'])
        model_slug = slugify_text(item['model_name'])

        try:
            with get_session() as session:
                # 1) Найти или создать CarMake
                make = session.query(CarMake).filter_by(slug=make_slug).first()
                if not make:
                    make = CarMake(name=item['make_name'], slug=make_slug)
                    session.add(make)
                    session.flush()  # чтобы получить make.id

                # 2) Найти модель **по глобальному** slug
                #    (в БД уникальный индекс только на slug)
                model = session.query(CarModel).filter_by(slug=model_slug).first()
                if not model:
                    model = CarModel(
                        make_id=make.id,
                        name=item['model_name'],
                        slug=model_slug
                    )
                    session.add(model)

        except IntegrityError:
            # если всё-таки сработал unique-констрейнт — просто пропустить
            spider.logger.debug(
                f"Skipped duplicate model slug: {item['model_name']} ({model_slug})"
            )

        return item
