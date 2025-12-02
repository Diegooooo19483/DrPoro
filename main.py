# main.py - VERSIÓN PARA RENDER
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sys

from database import engine, Base, get_db, create_tables
from routers import champions, items, associations, cvc, reports

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager para Render
    """
    logger.info("🚀 Iniciando Dr Poro API en Render...")

    # Crear tablas si no existen
    try:
        await create_tables()
    except Exception as e:
        logger.warning(f"⚠️  No se pudieron crear tablas: {e}")
        logger.info("⚠️  Las tablas pueden ya existir")

    yield

    logger.info("👋 Cerrando aplicación...")
    await engine.dispose()


# Crear aplicación
app = FastAPI(
    title="Dr Poro API",
    description="API para League of Legends",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Templates y static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(champions.router, prefix="/api/champions", tags=["Champions"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(associations.router, prefix="/api/associations", tags=["Associations"])
app.include_router(cvc.router, prefix="/api/cvc", tags=["CVC"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


# ========== RUTAS BÁSICAS ==========

@app.get("/")
async def root(request: Request):
    """Página principal"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Dr Poro API"}
    )


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check para Render"""
    try:
        # Probar conexión a DB
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "Dr Poro API",
            "database": "connected",
            "environment": "production"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Dr Poro API",
            "database": "disconnected",
            "error": str(e)
        }, 503


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint para ver variables de entorno"""
    import os
    return {
        "python_version": sys.version,
        "database_url": os.getenv("DATABASE_URL", "Not set"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "all_env_vars": {k: v for k, v in os.environ.items() if "DATABASE" in k or "POSTGRES" in k}
    }


# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Error en {request.method} {request.url.path}: {exc}")
    import traceback
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "path": request.url.path,
            "method": request.method
        }
    )