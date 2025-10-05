from database.models import Base
from config.settings import s

from alembic import context
from hydra.utils import instantiate

from logging.config import fileConfig
import logging

'''
Alembic docs: https://alembic.sqlalchemy.org/en/latest/index.html
Commands API: https://alembic.sqlalchemy.org/en/latest/api/commands.html
'''

config = context.config

if not logging.getLogger('__main__').hasHandlers():
    '''Alembic will disable existing loggers, so logging is disabled if loggers already exist'''
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = instantiate(s.db).engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True  # increases compatibility with SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
