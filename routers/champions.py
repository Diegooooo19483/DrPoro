from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
import models, schemas

router = APIRouter(prefix="/champions", tags=["Champions"])


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

    # Crear profile si viene
    if champion.profile:
        prof = models.Profile(
            champion_id=new_champion.id,
            descripcion=champion.profile.descripcion,
            historia=champion.profile.historia
        )
        db.add(prof)

    # Asociar ítems
    if champion.items:
        for item_id in champion.items:
            result_item = await db.execute(
                select(models.Item).where(models.Item.id == item_id)
            )
            item = result_item.scalar_one_or_none()
            if item:
                new_champion.items.append(item)

    await db.commit()
    await db.refresh(new_champion)

    return new_champion


@router.get("/", response_model=list[schemas.Champion])
async def list_champions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Champion))
    return result.scalars().all()


@router.get("/{champion_id}", response_model=schemas.Champion)
async def get_champion(champion_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Champion).where(models.Champion.id == champion_id)
    )
    champ = result.scalar_one_or_none()

    if not champ:
        raise HTTPException(404, "Campeón no encontrado")

    return champ


@router.put("/{champion_id}", response_model=schemas.Champion)
async def update_champion(champion_id: int, data: schemas.ChampionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Champion).where(models.Champion.id == champion_id)
    )
    champ = result.scalar_one_or_none()

    if not champ:
        raise HTTPException(404, "No encontrado")

    for k, v in data.dict(exclude_unset=True).items():
        if k == "items":
            champ.items.clear()
            for item_id in v:
                result_item = await db.execute(
                    select(models.Item).where(models.Item.id == item_id)
                )
                item = result_item.scalar_one_or_none()
                if item:
                    champ.items.append(item)
        else:
            setattr(champ, k, v)

    await db.commit()
    await db.refresh(champ)
    return champ


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
