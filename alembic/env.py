from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv
from alembic import context
from database.models import AutoAd, AutoAdHistory

# Загружаем переменные окружения из файла .env
load_dotenv()

# Берём строку подключения из .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

# Настройка SQLAlchemy URL
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем MetaData из SQLModel
target_metadata = SQLModel.metadata

# Настройка режима миграции
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=DATABASE_URL,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
