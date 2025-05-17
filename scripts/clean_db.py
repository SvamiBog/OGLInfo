#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


CLEAR_TABLES = [
    ("public", "autoad"),
    ("public", "autoadhistory"),
]


def load_database_url(env_path: str = ".env") -> str:
    """
    Загружает из .env строку подключения DATABASE_URL.
    Если файл или переменная не найдены — завершает работу с ошибкой.
    """
    if not os.path.exists(env_path):
        print(f"Ошибка: файл {env_path} не найден.", file=sys.stderr)
        sys.exit(1)

    load_dotenv(env_path)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Ошибка: переменная DATABASE_URL не установлена в .env.", file=sys.stderr)
        sys.exit(1)
    return db_url


def fetch_existing_tables(cursor) -> set[tuple[str, str]]:
    """
    Получает множество (schema, table) всех таблиц в БД,
    исключая системные схемы.
    """
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('information_schema', 'pg_catalog');
    """)
    return set(cursor.fetchall())


def truncate_specified_tables(db_url: str):
    """
    Подключается к БД, проверяет каждую таблицу из CLEAR_TABLES:
     - если есть — очищает TRUNCATE ... RESTART IDENTITY CASCADE
     - если нет  — выводит предупреждение
    """
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        existing = fetch_existing_tables(cur)
        if not CLEAR_TABLES:
            print("Список CLEAR_TABLES пуст — нечего очищать.")
            return

        for schema, table in CLEAR_TABLES:
            if (schema, table) in existing:
                q = sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY CASCADE;") \
                    .format(sql.Identifier(schema), sql.Identifier(table))
                cur.execute(q)
                print(f"[OK]   Очищена таблица {schema}.{table}")
            else:
                print(f"[WARN] Таблица {schema}.{table} не найдена — пропущена.")

        print("\nГотово: все указанные таблицы обработаны.")
    except Exception as e:
        print(f"Ошибка при выполнении: {e}", file=sys.stderr)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    db_url = load_database_url()
    truncate_specified_tables(db_url)
