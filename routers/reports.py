from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from models import Champion, Item, ChampionItem

router = APIRouter(prefix="/reports", tags=["Reports"])


# ---------------------------------------------------------
# TOP 10 CHAMPIONS POR WINRATE
# ---------------------------------------------------------
@router.get("/top-champions")
def top_champions(db: Session = Depends(get_db)):

    result = db.query(Champion) \
               .order_by(Champion.tasa_victoria.desc()) \
               .limit(10) \
               .all()

    return result


# ---------------------------------------------------------
# TOP 10 ITEMS POR PORCENTAJE DE USO
# ---------------------------------------------------------
@router.get("/top-items")
def top_items(db: Session = Depends(get_db)):

    result = db.query(Item) \
               .order_by(Item.porcentaje_uso.desc()) \
               .limit(10) \
               .all()

    return result


# ---------------------------------------------------------
# BUILD RECOMENDADA PARA UN CAMPEÓN
# (items + porcentaje_uso en ChampionItem)
# ---------------------------------------------------------
@router.get("/champion/{champion_id}/build")
def champion_build(champion_id: int, db: Session = Depends(get_db)):

    # Esta consulta devuelve tuplas: (Item, porcentaje_uso)
    result = (
        db.query(Item, ChampionItem.porcentaje_uso)
          .join(ChampionItem, ChampionItem.item_id == Item.id)
          .filter(ChampionItem.champion_id == champion_id)
          .order_by(ChampionItem.porcentaje_uso.desc())
          .all()
    )

    return result
