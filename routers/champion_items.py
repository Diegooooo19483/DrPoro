from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import crud, schemas, database
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/champion-items",
    tags=["Champion Items"]
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# lista items champ ============================================================
@router.get("/{champion_id}", response_class=HTMLResponse)
def get_items_for_champion(request: Request, champion_id: int, db: Session = Depends(get_db)):
    champion = crud.get_champion(db, champion_id)
    items = crud.get_items_for_champion(db, champion_id)

    return templates.TemplateResponse("champ_items/champion_items_list.html", {
        "request": request,
        "champion": champion,
        "items": items
    })


# AGREGAR ITEM ============================================================
@router.get("/{champion_id}/add", response_class=HTMLResponse)
def add_item_form(request: Request, champion_id: int, db: Session = Depends(get_db)):
    champion = crud.get_champion(db, champion_id)
    items = crud.list_items(db)

    return templates.TemplateResponse("champ_items/champion_items_add.html", {
        "request": request,
        "champion": champion,
        "items": items
    })


# PROCESAR POST ============================================================
@router.post("/{champion_id}/add")
def add_item_to_champion(
    request: Request,
    champion_id: int,
    item_id: int = Form(...),
    porcentaje_uso: float = Form(0.0),
    db: Session = Depends(get_db)
):
    crud.add_item_to_champion(db, champion_id, item_id, porcentaje_uso)
    return RedirectResponse(url=f"/champion-items/{champion_id}", status_code=303)
