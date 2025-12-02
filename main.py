# main.py - VERSIÓN SIMPLIFICADA
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from database import engine, Base
from routers import champions, items, associations, cvc, reports
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager para eventos de inicio/cierre.
    Crea las tablas al iniciar la aplicación.
    """
    print("🚀 Iniciando Dr Poro API...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️  Advertencia al inicializar DB: {e}")
        # Continúa sin las tablas (puede que ya existan)

    yield

    print("👋 Cerrando aplicación...")
    await engine.dispose()


# Crear aplicación FastAPI
app = FastAPI(
    title="Dr Poro API",
    description="API para gestión de campeones y items de League of Legends",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(champions.router, prefix="/api/champions", tags=["Champions"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(associations.router, prefix="/api/associations", tags=["Associations"])
app.include_router(cvc.router, prefix="/api/cvc", tags=["CVC"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/", include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
