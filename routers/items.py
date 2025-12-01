from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
import models, schemas

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si ya existe
    result = await db.execute(
        select(models.Item).where(models.Item.nombre == item.nombre)
    )
    exists = result.scalar_one_or_none()

    if exists:
        raise HTTPException(400, "El ítem ya existe")

    # Crear instancia
    new_item = models.Item(
        nombre=item.nombre,
        tipo=item.tipo,
        porcentaje_uso=item.porcentaje_uso,
        activo=True
    )

    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    return new_item


@router.get("/", response_model=list[schemas.Item])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Item))
    return result.scalars().all()


@router.get("/{item_id}", response_model=schemas.Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Item).where(models.Item.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(404, "No encontrado")

    return item
