from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from database import get_db
import models, schemas


router = APIRouter(prefix="/cvc", tags=["Campeón vs Campeón"])


# ----------------------------------------------------------
# CREAR CVC
# ----------------------------------------------------------
@router.post("/", response_model=schemas.CVC)
async def create_cvc(data: schemas.CVCCreate, db: AsyncSession = Depends(get_db)):

    if data.champion_id == data.oponente_id:
        raise HTTPException(400, "Un campeón no puede enfrentarse a sí mismo")

    # Verificar si ya existe relación
    result = await db.execute(
        select(models.ChampionVsChampion).where(
            and_(
                models.ChampionVsChampion.champion_id == data.champion_id,
                models.ChampionVsChampion.oponente_id == data.oponente_id
            )
        )
    )
    exists = result.scalar_one_or_none()
    if exists:
        raise HTTPException(400, "Ya existe el enfrentamiento")

    # Crear registro
    cvc = models.ChampionVsChampion(
        champion_id=data.champion_id,
        oponente_id=data.oponente_id,
        winrate=data.winrate,
    )

    db.add(cvc)
    await db.commit()

    # Recargar con relaciones
    refreshed = await db.execute(
        select(models.ChampionVsChampion)
        .options(
            selectinload(models.ChampionVsChampion.champion),
            selectinload(models.ChampionVsChampion.oponente)
        )
        .where(models.ChampionVsChampion.id == cvc.id)
    )

    return refreshed.scalar_one()


# ----------------------------------------------------------
# LISTAR CVC
# ----------------------------------------------------------
@router.get("/", response_model=list[schemas.CVC])
async def list_cvc(db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.ChampionVsChampion)
        .options(
            selectinload(models.ChampionVsChampion.champion),
            selectinload(models.ChampionVsChampion.oponente)
        )
    )

    return result.scalars().all()
