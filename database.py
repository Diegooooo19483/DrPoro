# database.py - VERSIÓN SIMPLIFICADA
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Cargar variables de entorno (Render las inyecta automáticamente)
DB_NAME = os.getenv("POSTGRESQL_ADDON_DB")
DB_USER = os.getenv("POSTGRESQL_ADDON_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_ADDON_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_ADDON_HOST")
DB_PORT = os.getenv("POSTGRESQL_ADDON_PORT")

# Construir URL de conexión
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Crear sessionmaker
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependencia para obtener sesión de base de datos"""
    async with async_session() as session:
        yield session