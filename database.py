import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # solo funciona local; en Clever Cloud ignora, usa env internas

# Variables de entorno de Clever Cloud
DB_NAME = os.getenv("POSTGRESQL_ADDON_DB")
DB_USER = os.getenv("POSTGRESQL_ADDON_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_ADDON_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_ADDON_HOST")
DB_PORT = os.getenv("POSTGRESQL_ADDON_PORT")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Base de modelos
Base = declarative_base()

# Engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,     # Cambia a True si quieres ver queries
    future=True
)

# Session async
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependencia para FastAPI
async def get_db():
    async with async_session() as session:
        yield session
