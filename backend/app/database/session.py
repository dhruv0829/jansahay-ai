from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from app.config import settings

# Handle SQLite specific parameters
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Keep the application split into two logical PostgreSQL schemas. SQLite has
# no equivalent schema support, so local/demo SQLite databases keep using the
# default schema.
SCHEMES_SCHEMA = "schemes" if engine.dialect.name == "postgresql" else None
CREDENTIALS_SCHEMA = "credentials" if engine.dialect.name == "postgresql" else None

def ensure_schemas(connection=None):
    """Create the app's PostgreSQL schemas when explicitly initializing DB tables."""
    if engine.dialect.name != "postgresql":
        return
    if connection is not None:
        connection.execute(CreateSchema("schemes", if_not_exists=True))
        connection.execute(CreateSchema("credentials", if_not_exists=True))
        return
    with engine.begin() as connection:
        connection.execute(CreateSchema("schemes", if_not_exists=True))
        connection.execute(CreateSchema("credentials", if_not_exists=True))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
