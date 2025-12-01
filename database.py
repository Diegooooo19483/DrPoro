import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Local; en Clever Cloud no se usa

# Variables de entorno de Clever Cloud
DB_NAME = os.getenv("POSTGRESQL_ADDON_DB")
DB_USER = os.getenv("POSTGRESQL_ADDON_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_ADDON_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_ADDON_HOST")
DB_PORT = os.getenv("POSTGRESQL_ADDON_PORT")

# URL SIN async
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Base de modelos
Base = declarative_base()

# Engine síncrono
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambia a True para debug
)

# Session síncrona
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependencia para FastAPI (sin async)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
