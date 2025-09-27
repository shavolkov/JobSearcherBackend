# alembic/env.py
import os, json
from alembic import context
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

# optional: only import boto3 if we intend to use Secrets Manager
try:
    import boto3
except Exception:
    boto3 = None

from app.db.models import Base
target_metadata = Base.metadata   # <-- keep this; don't overwrite later

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_url():
    # 1) explicit URL wins
    # return os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/postgres")
    url = os.getenv("DATABASE_URL")

    if url:

        return url

    # 2) build from Secrets Manager + optional env fallbacks
    sid = os.getenv("DB_SECRET_ID") or os.getenv("DB_SECRET_ARN")
    if sid and boto3:

        region = os.getenv("AWS_REGION", "us-east-2")
        sm = boto3.client("secretsmanager", region_name=region)
        s = json.loads(sm.get_secret_value(SecretId=sid)["SecretString"])

        user = s.get("username")
        pwd  = s.get("password")

        # RDS-managed secret might not include these; allow env overrides
        host = s.get("host") or os.getenv("DB_HOST") or os.getenv("RDS_ENDPOINT")
        port = str(s.get("port") or os.getenv("DB_PORT", "5432"))
        db   = s.get("dbname") or os.getenv("DB_NAME", "postgres")

        if not (user and pwd and host):
            raise RuntimeError(
                "DB creds incomplete. Provide DB_HOST/DB_PORT/DB_NAME envs or use a secret that includes host/port/dbname."
            )

        driver = os.getenv("DB_DRIVER", "psycopg")  # use 'psycopg2' if that’s your driver
        return f"postgresql+{driver}://{user}:{pwd}@{host}:{port}/{db}?sslmode=require"

    # 3) final fallback: whatever's in alembic.ini

    return config.get_main_option("sqlalchemy.url")

# ensure SQLAlchemy sees the final URL
config.set_main_option("sqlalchemy.url", get_url())
# Interpret the config file for Python logging.
# This line sets up loggers basically.


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
