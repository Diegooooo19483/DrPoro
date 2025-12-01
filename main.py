# main.py
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db, create_tables
from routers import champions, items, associations, cvc, reports

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager para eventos de inicio/cierre de la aplicación.

    - Al iniciar: crea las tablas en la base de datos
    - Al cerrar: limpia recursos
    """
    print("🚀 Iniciando aplicación Dr Poro API...")

    # Crear tablas en la base de datos
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        # No lanzamos excepción para permitir que la app arranque
        # y mostrar una página de error más amigable

    yield  # La aplicación corre aquí

    print("👋 Cerrando aplicación...")
    # Cerrar conexiones de la base de datos
    await engine.dispose()


app = FastAPI(
    title="Dr Poro API",
    description="API para gestión de campeones y items de League of Legends",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(champions.router, prefix="/api/champions", tags=["Champions"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(associations.router, prefix="/api/associations", tags=["Associations"])
app.include_router(cvc.router, prefix="/api/cvc", tags=["CVC"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


# ==================== RUTAS DE DEBUG Y MONITOREO ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Dr Poro API - Inicio"}
    )


@app.get("/health")
async def health_check():
    """Endpoint de salud para monitoreo"""
    return {
        "status": "healthy",
        "service": "Dr Poro API",
        "version": "1.0.0"
    }


@app.get("/debug/database")
async def debug_database(db: AsyncSession = Depends(get_db)):
    """Verificar estado de la conexión a base de datos"""
    try:
        # Probar conexión con una consulta simple
        result = await db.execute("SELECT version(), current_database(), current_user")
        row = result.fetchone()

        return {
            "status": "connected",
            "database": {
                "version": row[0] if row else "N/A",
                "name": row[1] if row else "N/A",
                "user": row[2] if row else "N/A"
            },
            "message": "Conexión a PostgreSQL exitosa"
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "message": "Error de conexión a la base de datos"
        }


@app.get("/debug/environment")
async def debug_environment():
    """Mostrar variables de entorno relevantes (sin contraseñas)"""
    env_vars = {
        "POSTGRESQL_ADDON_DB": os.getenv("POSTGRESQL_ADDON_DB"),
        "POSTGRESQL_ADDON_USER": os.getenv("POSTGRESQL_ADDON_USER"),
        "POSTGRESQL_ADDON_HOST": os.getenv("POSTGRESQL_ADDON_HOST"),
        "POSTGRESQL_ADDON_PORT": os.getenv("POSTGRESQL_ADDON_PORT"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "POSTGRESQL_ADDON_URL": os.getenv("POSTGRESQL_ADDON_URL"),
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION"),
        "RENDER": os.getenv("RENDER", "false"),
        "PORT": os.getenv("PORT", "10000"),
    }

    # Ocultar valores sensibles
    sensitive = ["POSTGRESQL_ADDON_PASSWORD"]
    for key in env_vars.keys():
        if "PASSWORD" in key.upper() and env_vars[key]:
            env_vars[key] = "******"
        if "URL" in key.upper() and env_vars[key] and "@" in env_vars[key]:
            # Ocultar contraseña en URLs
            url = env_vars[key]
            if "://" in url:
                protocol, rest = url.split("://", 1)
                if "@" in rest:
                    user_pass, server = rest.split("@", 1)
                    if ":" in user_pass:
                        user, _ = user_pass.split(":", 1)
                        env_vars[key] = f"{protocol}://{user}:******@{server}"

    return {
        "environment": env_vars,
        "missing_variables": [k for k, v in env_vars.items() if v is None],
        "all_loaded": all(v is not None for k, v in env_vars.items() if "PASSWORD" not in k.upper())
    }


@app.get("/api/status")
async def api_status(db: AsyncSession = Depends(get_db)):
    """Estado completo de la API"""
    try:
        # Probar conexión a DB
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "api": "Dr Poro API",
        "status": "running",
        "database": db_status,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Página principal"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/debug/database", "method": "GET", "description": "Debug DB"},
            {"path": "/debug/environment", "method": "GET", "description": "Debug env vars"},
            {"path": "/api/champions", "method": "GET", "description": "Listar campeones"},
            {"path": "/api/items", "method": "GET", "description": "Listar items"},
            {"path": "/api/reports", "method": "GET", "description": "Generar reportes"},
        ]
    }


# ==================== MANEJO DE ERRORES ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )


@app.get("/favicon.ico")
async def favicon():
    """Evitar error 404 por favicon"""
    return ""