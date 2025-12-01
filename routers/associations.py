from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
import models

router = APIRouter(prefix="/assoc", tags=["Asociaciones"])

@router.post("/{champion_id}/add-item/{item_id}")
async def add_item(champion_id: int, item_id: int, db: AsyncSession = Depends(get_db)):
    # Obtener campeón
    result_champ = await db.execute(
        select(models.Champion).where(models.Champion.id == champion_id)
    )
    champ = result_champ.scalar_one_or_none()

    # Obtener ítem
    result_item = await db.execute(
        select(models.Item).where(models.Item.id == item_id)
    )
    item = result_item.scalar_one_or_none()

    if not champ or not item:
        raise HTTPException(404, "Campeón o ítem no encontrado")

    champ.items.append(item)
    await db.commit()
    return {"message": "Añadido correctamente"}


@router.delete("/{champion_id}/remove-item/{item_id}")
async def remove_item(champion_id: int, item_id: int, db: AsyncSession = Depends(get_db)):
    # Obtener campeón
    result_champ = await db.execute(
        select(models.Champion).where(models.Champion.id == champion_id)
    )
    champ = result_champ.scalar_one_or_none()

    # Obtener ítem
    result_item = await db.execute(
        select(models.Item).where(models.Item.id == item_id)
    )
    item = result_item.scalar_one_or_none()

    if not champ or not item:
        raise HTTPException(404, "Campeón o ítem no encontrado")

    if item in champ.items:
        champ.items.remove(item)
        await db.commit()

    return {"message": "Eliminado correctamente"}
