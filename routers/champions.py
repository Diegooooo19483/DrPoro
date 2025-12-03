from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud, schemas, database
from typing import Optional
import models

router = APIRouter(prefix="/champions", tags=["Champions"])
templates = Jinja2Templates(directory="templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== VISTAS HTML ==========

@router.get("/list", response_class=HTMLResponse)
def list_champions_page(request: Request, rol: Optional[str] = None, db: Session = Depends(get_db)):
    champions = [c for c in crud.list_champions_by_winrate(db, rol) if c.activo]
    return templates.TemplateResponse("champion/champions_list.html", {
        "request": request,
        "champions": champions,
        "selected_rol": rol,
        "roles": ["Top", "JG", "Mid", "Adc", "Sup"]
    })


@router.get("/deleted", response_class=HTMLResponse)
def list_deleted_champions_page(request: Request, db: Session = Depends(get_db)):
    deleted = [c for c in crud.list_champions(db, include_inactive=True) if not c.activo]
    return templates.TemplateResponse("champion/champions_deleted.html", {
        "request": request,
        "champions": deleted
    })


@router.get("/new", response_class=HTMLResponse)
def new_champion_form(request: Request):
    return templates.TemplateResponse("champion/champion_create.html", {"request": request})


@router.post("/new")
def submit_new_champion(
        nombre: str = Form(...), rol: str = Form(...), tasa_victoria: float = Form(50.0),
        tasa_seleccion: float = Form(0.0), tasa_baneo: float = Form(0.0),
        activo: Optional[str] = Form("on"), db: Session = Depends(get_db)
):
    new_champ = models.Champion(
        nombre=nombre, rol=rol, tasa_victoria=tasa_victoria,
        tasa_seleccion=tasa_seleccion, tasa_baneo=tasa_baneo,
        activo=activo == "on"
    )
    db.add(new_champ)
    db.commit()
    return RedirectResponse("/champions/list", status_code=302)


@router.get("/{champion_id}/view", response_class=HTMLResponse)
def view_champion(champion_id: int, request: Request, db: Session = Depends(get_db)):
    champion = crud.get_champion(db, champion_id) or raise_404()
    items_con_porcentaje = [(ci, item) for item in champion.items
                            for ci in champion.champion_items if ci.item_id == item.id]
    return templates.TemplateResponse("champion/champion_detail.html", {
        "request": request, "champion": champion,
        "all_items": crud.list_items(db), "items_con_porcentaje": items_con_porcentaje
    })


@router.get("/{champion_id}/edit", response_class=HTMLResponse)
def edit_champion_form(champion_id: int, request: Request, db: Session = Depends(get_db)):
    champion = crud.get_champion(db, champion_id) or raise_404()
    return templates.TemplateResponse("champion/champion_edit.html", {
        "request": request, "champion": champion
    })


@router.post("/{champion_id}/edit")
def submit_edit_champion(
        champion_id: int, nombre: str = Form(...), rol: str = Form(...),
        tasa_victoria: float = Form(50.0), tasa_seleccion: float = Form(0.0),
        tasa_baneo: float = Form(0.0), activo: Optional[str] = Form("on"),
        db: Session = Depends(get_db)
):
    champ = crud.get_champion(db, champion_id) or raise_404()
    if rol not in ["Top", "JG", "Mid", "Adc", "Sup"]:
        raise HTTPException(400, detail=f"Rol inválido: {rol}")

    champ.__dict__.update({
        "nombre": nombre, "rol": rol, "tasa_victoria": tasa_victoria,
        "tasa_seleccion": tasa_seleccion, "tasa_baneo": tasa_baneo,
        "activo": activo == "on"
    })
    db.commit()
    return RedirectResponse("/champions/list", status_code=302)


# ========== ACCIONES ==========

@router.post("/{champion_id}/add-item")
def add_item_to_champion(
        champion_id: int, item_id: int = Form(...),
        porcentaje_uso: float = Form(0.0), db: Session = Depends(get_db)
):
    champion = crud.get_champion(db, champion_id) or raise_404()
    existing = next((ci for ci in champion.champion_items if ci.item_id == item_id), None)

    if existing:
        existing.porcentaje_uso = porcentaje_uso
    else:
        db.add(models.ChampionItem(
            champion_id=champion_id, item_id=item_id, porcentaje_uso=porcentaje_uso
        ))
    db.commit()
    return RedirectResponse(f"/champions/{champion_id}/view", status_code=302)


@router.post("/{champion_id}/delete")
def delete_champion(champion_id: int, db: Session = Depends(get_db)):
    champ = crud.get_champion(db, champion_id) or raise_404()
    champ.activo = False
    db.commit()
    return RedirectResponse("/champions/list", status_code=303)


@router.post("/{champion_id}/activate")
def activate_champion(champion_id: int, db: Session = Depends(get_db)):
    champ = crud.get_champion(db, champion_id) or raise_404()
    champ.activo = True
    db.commit()
    return RedirectResponse("/champions/deleted", status_code=303)


# ========== API JSON ==========

@router.get("/", response_model=list[schemas.Champion])
def list_champions(skip: int = 0, limit: int = 100, include_inactive: bool = False, db: Session = Depends(get_db)):
    return crud.list_champions(db, skip, limit, include_inactive)


@router.get("/api/deleted", response_model=list[schemas.Champion])
def list_deleted_champions_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return [c for c in crud.list_champions(db, skip, limit, True) if not c.activo]


@router.get("/{champion_id}", response_model=schemas.Champion)
def get_champion(champion_id: int, db: Session = Depends(get_db)):
    return crud.get_champion(db, champion_id) or raise_404()


@router.get("/by-name/{name}", response_model=schemas.Champion)
def get_champion_by_name(name: str, db: Session = Depends(get_db)):
    return crud.get_champion_by_name(db, name) or raise_404()


@router.post("/", response_model=schemas.Champion)
def create_champion(champion: schemas.ChampionCreate, db: Session = Depends(get_db)):
    return crud.create_champion(db, champion)


@router.put("/{champion_id}", response_model=schemas.Champion)
def update_champion(champion_id: int, champion: schemas.ChampionUpdate, db: Session = Depends(get_db)):
    return crud.update_champion(db, champion_id, champion) or raise_404()


# ========== UTILIDADES ==========

def raise_404():
    raise HTTPException(404, "Champion not found")


@router.get("/", include_in_schema=False)
def redirect_to_list():
    return RedirectResponse("/champions/list", status_code=302)