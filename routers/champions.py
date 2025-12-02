from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import get_db
import models, schemas


router = APIRouter(prefix="/champions", tags=["Champions"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
async def create_champion_form(request: Request):
    return templates.TemplateResponse("create_champion.html", {"request": request})


@router.post("/create", response_class=HTMLResponse)
async def create_champion_form_post(
    request: Request,
    nombre: str = Form(...),
    rol: str = Form(...),
    tasa_victoria: float = Form(...),
    tasa_seleccion: float = Form(...),
    tasa_baneo: float = Form(...),
    descripcion: str = Form(""),
    historia: str = Form(""),
    items: str = Form("")
):
    # Convertir items: "1,2,3" → [1,2,3]
    item_ids = [int(x.strip()) for x in items.split(",")] if items else []

    payload = {
        "nombre": nombre,
        "rol": rol,
        "tasa_victoria": tasa_victoria,
        "tasa_seleccion": tasa_seleccion,
        "tasa_baneo": tasa_baneo,
        "profile": {
            "descripcion": descripcion,
            "historia": historia
        },
        "items": item_ids
    }

    # Reusar tu endpoint API
    from fastapi.encoders import jsonable_encoder
    champion_data = schemas.ChampionCreate(**jsonable_encoder(payload))

    return await create_champion(champion_data)
# ----------------------------------------------------------
# CREAR
# ----------------------------------------------------------
@router.post("/", response_model=schemas.Champion)
async def create_champion(champion: schemas.ChampionCreate, db: AsyncSession = Depends(get_db)):

    # Validar duplicado
    result = await db.execute(
        select(models.Champion).where(models.Champion.nombre == champion.nombre)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(400, "El campeón ya existe")

    # Crear campeón
    new_champion = models.Champion(
        nombre=champion.nombre,
        rol=champion.rol,
        tasa_victoria=champion.tasa_victoria,
        tasa_seleccion=champion.tasa_seleccion,
        tasa_baneo=champion.tasa_baneo,
        activo=True
    )
    db.add(new_champion)
    await db.commit()
    await db.refresh(new_champion)

    # Crear profile
    if champion.profile:
        prof = models.Profile(
            champion_id=new_champion.id,
            descripcion=champion.profile.descripcion,
            historia=champion.profile.historia
        )
        db.add(prof)

    # Asociar items
    if champion.items:
        items_result = await db.execute(
            select(models.Item).where(models.Item.id.in_(champion.items))
        )
        items = items_result.scalars().all()
        new_champion.items.extend(items)

    await db.commit()

    # Recargar con relaciones
    refreshed = await db.execute(
        select(models.Champion)
        .options(selectinload(models.Champion.items),
                 selectinload(models.Champion.profile))
        .where(models.Champion.id == new_champion.id)
    )
    return refreshed.scalar_one()


# ----------------------------------------------------------
# LISTAR
# ----------------------------------------------------------
@router.get("/", response_model=list[schemas.Champion])
async def list_champions(db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Champion)
        .options(
            selectinload(models.Champion.items),
            selectinload(models.Champion.profile)
        )
    )
    return result.scalars().all()


# ----------------------------------------------------------
# OBTENER UNO
# ----------------------------------------------------------
@router.get("/{champion_id}", response_model=schemas.Champion)
async def get_champion(champion_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Champion)
        .options(
            selectinload(models.Champion.items),
            selectinload(models.Champion.profile)
        )
        .where(models.Champion.id == champion_id)
    )

    champ = result.scalar_one_or_none()
    if not champ:
        raise HTTPException(404, "Campeón no encontrado")

    return champ


# ----------------------------------------------------------
# ACTUALIZAR
# ----------------------------------------------------------
@router.put("/{champion_id}", response_model=schemas.Champion)
async def update_champion(champion_id: int, data: schemas.ChampionUpdate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Champion)
        .options(selectinload(models.Champion.items))
        .where(models.Champion.id == champion_id)
    )
    champ = result.scalar_one_or_none()

    if not champ:
        raise HTTPException(404, "No encontrado")

    payload = data.dict(exclude_unset=True)

    # Si vienen items → reemplazar
    if "items" in payload:
        new_items_result = await db.execute(
            select(models.Item).where(models.Item.id.in_(payload["items"]))
        )
        champ.items = new_items_result.scalars().all()
        del payload["items"]

    # Actualizar campos simples
    for k, v in payload.items():
        setattr(champ, k, v)

    await db.commit()

    # Recargar con relaciones
    refreshed = await db.execute(
        select(models.Champion)
        .options(selectinload(models.Champion.items),
                 selectinload(models.Champion.profile))
        .where(models.Champion.id == champion_id)
    )
    return refreshed.scalar_one()


# ----------------------------------------------------------
# ELIMINAR
# ----------------------------------------------------------
@router.delete("/{champion_id}")
async def delete_champion(champion_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Champion).where(models.Champion.id == champion_id)
    )
    champ = result.scalar_one_or_none()

    if not champ:
        raise HTTPException(404, "No encontrado")

    await db.delete(champ)
    await db.commit()

    return {"message": "Eliminado correctamente"}
