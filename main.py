from fastapi import FastAPI,  Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import get_db
from fastapi.templating import Jinja2Templates
from database import init_db
from fastapi.responses import HTMLResponse
from routers import champions, items, champion_items, cvc, userprofiles
import crud

app = FastAPI(title="Drporo")

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    init_db()



# Routers
app.include_router(champions.router)
app.include_router(items.router)
app.include_router(champion_items.router)
app.include_router(cvc.router)

app.include_router(userprofiles.router)

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})

@app.get("/search")
def search(request: Request, q: str = "", db: Session = Depends(get_db)):
    champions = []
    items = []
    if q:
        # Busca campeones que contengan la query en el nombre
        champions = db.query(crud.models.Champion).filter(crud.models.Champion.nombre.ilike(f"%{q}%")).all()
        # Busca items que contengan la query en el nombre
        items = db.query(crud.models.Item).filter(crud.models.Item.nombre.ilike(f"%{q}%")).all()
    return templates.TemplateResponse("main/search.html", {
        "request": request,
        "query": q,
        "champions": champions,
        "items": items
    })