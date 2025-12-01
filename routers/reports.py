from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Champion, Item, ChampionItem

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/top-champions")
async def top_champions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Champion).order_by(Champion.tasa_victoria.desc()).limit(10)
    )
    return result.scalars().all()


@router.get("/top-items")
async def top_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Item).order_by(Item.porcentaje_uso.desc()).limit(10)
    )
    return result.scalars().all()


@router.get("/champion/{champion_id}/build")
async def champion_build(champion_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Item, ChampionItem.porcentaje_uso)
        .join(ChampionItem, ChampionItem.item_id == Item.id)
        .where(ChampionItem.champion_id == champion_id)
        .order_by(ChampionItem.porcentaje_uso.desc())
    )
    return result.all()
