from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Charger la configuration Alembic
config = context.config

# Configurer les logs depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import de tous les modèles pour l'autogenerate ────────────────────────────
# L'ordre d'import est important : les modèles référencés (User, Referendum)
# doivent être chargés avant les modèles qui les référencent (Vote, Argument).
import agora.models  # noqa: F401 — importe tous les modèles via __init__.py
from agora.core.database import Base
from agora.core.config import settings

# Surcharger la sqlalchemy.url depuis les settings Python (lit le .env)
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Migrations en mode 'offline' (génération SQL sans connexion active)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Rendre les noms de contraintes reproductibles
        render_as_batch=True,  # nécessaire pour SQLite (ALTER TABLE limité)
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migrations en mode 'online' (connexion active)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # nécessaire pour SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
