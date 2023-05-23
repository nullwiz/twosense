import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user, db_name = "postgres", "locations"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

# For creating initial tables. not used in docker


def get_sync_postgres_uri():
    host = "127.0.0.1"
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user, db_name = "postgres", "locations"
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "127.0.0.1")
    port = 6379
    return {"host": host, "port": port}


def get_repo_orm():
    return 'sqlalchemy'
