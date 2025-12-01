# database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

# Variables con nombres CORRECTOS (ADDON, no ADRON)
DB_NAME = os.getenv("POSTGRESQL_ADDON_DB")
DB_USER = os.getenv("POSTGRESQL_ADDON_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_ADDON_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_ADDON_HOST")
DB_PORT = os.getenv("POSTGRESQL_ADDON_PORT")

# Verificación de variables cargadas
print("=" * 50)
print("📡 VERIFICACIÓN DE VARIABLES DE BASE DE DATOS")
print("=" * 50)

variables_info = [
    ("POSTGRESQL_ADDON_DB", DB_NAME),
    ("POSTGRESQL_ADDON_USER", DB_USER),
    ("POSTGRESQL_ADDON_HOST", DB_HOST),
    ("POSTGRESQL_ADDON_PORT", DB_PORT),
]

for var_name, var_value in variables_info:
    if var_value:
        print(f"✅ {var_name}: {var_value}")
    else:
        print(f"❌ {var_name}: NO DEFINIDA")

print("-" * 50)

# Verificar que todas las variables requeridas estén presentes
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    missing = []
    if not DB_NAME: missing.append("POSTGRESQL_ADDON_DB")
    if not DB_USER: missing.append("POSTGRESQL_ADDON_USER")
    if not DB_PASSWORD: missing.append("POSTGRESQL_ADDON_PASSWORD")
    if not DB_HOST: missing.append("POSTGRESQL_ADDON_HOST")
    if not DB_PORT: missing.append("POSTGRESQL_ADDON_PORT")

    error_msg = f"Faltan variables de entorno: {', '.join(missing)}"
    print(f"🚨 ERROR CRÍTICO: {error_msg}")
    print("⚠️  Asegúrate de que en Render las variables se llamen:")
    print("   - POSTGRESQL_ADDON_DB (no POSTGRESQL_ADRON_DB)")
    print("   - POSTGRESQL_ADDON_USER (no POSTGRESQL_ADRON_USER)")
    print("   - POSTGRESQL_ADDON_PASSWORD (no POSTGRESQL_ADRON_PASSWORD)")
    print("   - POSTGRESQL_ADDON_HOST (no POSTGRESQL_ADRON_HOST)")
    print("   - POSTGRESQL_ADDON_PORT (no POSTGRESQL_ADRON_PORT)")
    raise ValueError(error_msg)

# Construir URL de conexión para asyncpg
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Mostrar URL (ocultando contraseña)
safe_url = DATABASE_URL.replace(DB_PASSWORD, "******") if DB_PASSWORD else DATABASE_URL
print(f"🔗 URL de conexión: {safe_url}")
print("=" * 50)

# Crear motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Cambia a False en producción
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True
)

# Crear sessionmaker asíncrono
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


# Función de dependencia para FastAPI
async def get_db() -> AsyncSession:
    """
    Proveedor de sesión de base de datos para rutas FastAPI.

    Uso:
    @app.get("/items")
    async def read_items(db: AsyncSession = Depends(get_db)):
        # usar db para consultas
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Función para crear tablas (opcional, ya lo haces en lifespan)
async def create_tables():
    """Crear todas las tablas definidas en los modelos"""
    print("🗃️  Creando tablas en la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas exitosamente")