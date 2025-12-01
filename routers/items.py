from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/items", tags=["Items"])


# -------------------------------------------------------------
# CREAR ITEM
# -------------------------------------------------------------
@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):

    # Verificar si ya existe
    exists = db.query(models.Item).filter(
        models.Item.nombre == item.nombre
    ).first()

    if exists:
        raise HTTPException(400, "El ítem ya existe")

    new_item = models.Item(
        nombre=item.nombre,
        tipo=item.tipo,
        porcentaje_uso=item.porcentaje_uso,
        activo=True
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# -------------------------------------------------------------
# LISTAR ITEMS
# -------------------------------------------------------------
@router.get("/", response_model=list[schemas.Item])
def get_items(db: Session = Depends(get_db)):

    return db.query(models.Item).all()


# -------------------------------------------------------------
# OBTENER ITEM POR ID
# -------------------------------------------------------------
@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):

    item = db.query(models.Item).filter(
        models.Item.id == item_id
    ).first()

    if not item:
        raise HTTPException(404, "No encontrado")

    return item
