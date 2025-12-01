from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/assoc", tags=["Asociaciones"])


@router.post("/{champion_id}/add-item/{item_id}")
def add_item(champion_id: int, item_id: int, db: Session = Depends(get_db)):

    # Obtener campeón
    champ = db.query(models.Champion).filter(models.Champion.id == champion_id).first()

    # Obtener ítem
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not champ or not item:
        raise HTTPException(404, "Campeón o ítem no encontrado")

    champ.items.append(item)
    db.commit()

    return {"message": "Añadido correctamente"}


@router.delete("/{champion_id}/remove-item/{item_id}")
def remove_item(champion_id: int, item_id: int, db: Session = Depends(get_db)):

    # Obtener campeón
    champ = db.query(models.Champion).filter(models.Champion.id == champion_id).first()

    # Obtener ítem
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not champ or not item:
        raise HTTPException(404, "Campeón o ítem no encontrado")

    if item in champ.items:
        champ.items.remove(item)
        db.commit()

    return {"message": "Eliminado correctamente"}
