# database.py - VERSIÓN PARA RENDER
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

# Render inyecta DATABASE_URL automáticamente
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no hay DATABASE_URL, usar variables individuales
if not DATABASE_URL:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")

    if all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
        DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Para desarrollo local
        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/drporo_local"

# Convertir a asyncpg si es necesario
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Para SSL en Render (requerido)
if "render.com" in DATABASE_URL or "onrender.com" in DATABASE_URL:
    DATABASE_URL += "?ssl=true"

logger.info(f"🔗 Conectando a base de datos...")

# Crear motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Muestra SQL en logs - útil para debug
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require" if "render.com" in DATABASE_URL else None
    }
)

# Session maker
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db():
    """Dependencia para obtener sesión de DB"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Función para crear tablas
async def create_tables():
    """Crear todas las tablas al inicio"""
    logger.info("🗃️  Creando tablas en la base de datos...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")