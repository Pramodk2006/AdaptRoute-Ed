"""
Alembic environment configuration.
Reads DATABASE_URL from environment and enables autogenerate against
all ORM models imported via app.models.
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Load FastAPI app config to get DATABASE_URL
from app.config import get_settings
from app.database import Base

# Import all models so Alembic's autogenerate sees them
import app.models  # noqa: F401

settings = get_settings()

# Alembic Config object (provides access to alembic.ini values)
config = context.config

# Set the SQLAlchemy URL from our app settings (overrides blank alembic.ini value)
# Escape '%' as '%%' to prevent configparser from failing on URL-encoded passwords (e.g. %40)
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL).replace("%", "%%"))

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata of our Base — used for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the live database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
