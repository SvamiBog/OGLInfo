# scripts/crawl.py
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 1) добавить корень, чтобы работал import database.db_config
sys.path.insert(0, BASE_DIR)

if '--project' in sys.argv:
    idx = sys.argv.index('--project') + 1
    proj = sys.argv[idx]
    # внешний каталог проекта, где лежит scrapy.cfg
    project_root = os.path.join(BASE_DIR, 'parsers', proj)
    # переключаемся в него — Scrapy найдёт свой scrapy.cfg и спайдеры
    os.chdir(project_root)
    # добавляем этот каталог в sys.path для импорта settings и spiders
    sys.path.insert(0, project_root)
    os.environ['SCRAPY_SETTINGS_MODULE'] = f'{proj}.settings'

import argparse
from scrapy.cmdline import execute

def main():
    parser = argparse.ArgumentParser(description="Запуск Scrapy-пауков из разных проектов")
    parser.add_argument('--project', required=True,
                        choices=['oglinfo_scraper','makes_models_scraper'],
                        help='Название Scrapy-проекта (папка с scrapy.cfg)')
    parser.add_argument('--spider', required=True, help='Имя паука')
    args = parser.parse_args()

    print(f"▶ Запускаем паука '{args.spider}' из проекта '{args.project}' (cwd={os.getcwd()})")
    execute(['scrapy', 'crawl', args.spider])

if __name__ == '__main__':
    main()
