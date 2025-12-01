from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from database import engine, Base
from routers import champions, items, associations, cvc, reports

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Dr Poro API",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(champions.router)
app.include_router(items.router)
app.include_router(associations.router)
app.include_router(cvc.router)
app.include_router(reports.router)
