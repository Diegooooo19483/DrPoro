from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from database import get_db, init_db
from routers import champions, items, champion_items, cvc, userprofiles
import crud

app = FastAPI(title="Drporo")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except OperationalError:
        pass


# Routers
app.include_router(champions.router)
app.include_router(items.router)
app.include_router(champion_items.router)
app.include_router(cvc.router)
app.include_router(userprofiles.router)


# Root
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


# Search
@app.get("/search")
def search(request: Request, q: str = "", db: Session = Depends(get_db)):
    champions_result = []
    items_result = []

    if q:
        champions_result = (
            db.query(crud.models.Champion)
            .filter(crud.models.Champion.nombre.ilike(f"%{q}%"))
            .all()
        )
        items_result = (
            db.query(crud.models.Item)
            .filter(crud.models.Item.nombre.ilike(f"%{q}%"))
            .all()
        )

    return templates.TemplateResponse("main/search.html", {
        "request": request,
        "query": q,
        "champions": champions_result,
        "items": items_result
    })
