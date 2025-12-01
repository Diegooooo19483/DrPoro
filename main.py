from database import get_db
from database import engine, Base
from routers import champions, items, associations, cvc, reports
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Dr. Poro - API de Estadísticas de LoL")


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

started = False

@app.on_event("startup")
async def startup():
    global started
    if started:
        return
    started = True

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Routers
app.include_router(champions.router)
app.include_router(items.router)
app.include_router(associations.router)
app.include_router(cvc.router)
app.include_router(reports.router)
