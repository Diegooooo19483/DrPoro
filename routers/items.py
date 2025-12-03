from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import crud, schemas, database

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------
# 🔹 HTML – Listar Items
# -----------------------------------------------
@router.get("/", response_class=HTMLResponse)
def list_items_page(request: Request, db: Session = Depends(get_db)):
    items = crud.list_items(db)
    return templates.TemplateResponse(
        "items/items_list.html",
        {"request": request, "items": items}
    )


# -----------------------------------------------
# 🔹 HTML – Ver un Item
# -----------------------------------------------
@router.get("/{item_id}/view", response_class=HTMLResponse)
def view_item_page(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        return RedirectResponse(url="/items", status_code=302)

    return templates.TemplateResponse(
        "items/item_detail.html",
        {"request": request, "item": item}
    )


# -----------------------------------------------
# TEMPLATE: FORM PARA CREAR
# -----------------------------------------------
@router.get("/new", response_class=HTMLResponse)
def new_champion_form(request: Request):
    return templates.TemplateResponse("items/item_create.html", {
        "request": request
    })


# -----------------------------------------------
# FORM POST CREAR DESDE HTML
# -----------------------------------------------
@router.post("/new", response_class=HTMLResponse)
def create_item_from_form(
    request: Request,
    nombre: str = Form(...),
    tipo: str = Form(""),
    porcentaje_uso: float = Form(0.0),
    db: Session = Depends(get_db)
):
    new_item = schemas.ItemCreate(
        nombre=nombre,
        tipo=tipo,
        porcentaje_uso=porcentaje_uso
    )

    crud.create_item(db, new_item)

    return RedirectResponse(url="/items/", status_code=302)


# ------------------------------
# HTML – Editar Item
# ------------------------------
@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_item_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        return RedirectResponse(url="/items", status_code=302)
    return templates.TemplateResponse("items/item_edit.html", {
        "request": request,
        "item": item
    })

@router.post("/{item_id}/edit")
def update_item_from_form(item_id: int,
                          nombre: str = Form(...),
                          tipo: str = Form(...),
                          porcentaje_uso: float = Form(...),
                          db: Session = Depends(get_db)):
    item_data = schemas.ItemUpdate(nombre=nombre, tipo=tipo, porcentaje_uso=porcentaje_uso)
    crud.update_item(db, item_id, item_data)
    return RedirectResponse(url=f"/items/{item_id}/view", status_code=302)


# ------------------------------
# HTML – Borrar Item
# ------------------------------
@router.post("/{item_id}/delete")
def delete_item_from_form(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.soft_delete_item(db, item_id)
    # Si no existe, redirige a la lista de items
    if not db_item:
        return RedirectResponse("/items", status_code=302)
    # Redirige a la lista de items después de borrar
    return RedirectResponse("/items", status_code=302)
