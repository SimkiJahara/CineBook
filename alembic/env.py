from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 💡 FIX 1: Import application settings and database Base
from app.core.config import settings 
from app.core.db import Base 

# 💡 FIX 2: Import ALL models so Alembic can discover them for autogenerate
from app.models.users import User
from app.models.theatreowner import TheatreOwner
from app.models.theatre import Theatre
from app.models.buyer import Buyer
from app.models.superadmin import Superadmin
from app.models.movie import Movie
from app.models.screen import Screen
from app.models.show import Screening
from app.models.seat import ShowSeat, Seat, Booking, BookedSeat
from app.models.promocode import Promocode # <-- NEW MODEL IMPORT


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 💡 FIX 3: Set target_metadata to the Base.metadata object 
# so Alembic can find all your model definitions
target_metadata = Base.metadata

# 💡 FIX 4: Set SQLAlchemy URL from application settings (Critical for connection)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()