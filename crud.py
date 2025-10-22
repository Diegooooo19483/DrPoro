# crud.py
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import and_
from typing import List, Optional

# Champions
def get_champion(db: Session, champion_id: int):
    return db.query(models.Champion).filter(models.Champion.id == champion_id).first()

def get_champion_by_name(db: Session, nombre: str):
    return db.query(models.Champion).filter(models.Champion.nombre == nombre).first()

def list_champions(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool=False):
    q = db.query(models.Champion)
    if not include_inactive:
        q = q.filter(models.Champion.activo == True)
    return q.offset(skip).limit(limit).all()

def create_champion(db: Session, champion: schemas.ChampionCreate):
    db_champ = models.Champion(
        nombre=champion.nombre,
        rol=champion.rol,
        tasa_victoria=champion.tasa_victoria,
        tasa_seleccion=champion.tasa_seleccion,
        tasa_baneo=champion.tasa_baneo,
    )
    if champion.profile:
        db_champ.profile = models.Profile(descripcion=champion.profile.descripcion, historia=champion.profile.historia)
    db.add(db_champ)
    db.commit()
    db.refresh(db_champ)
    return db_champ

def update_champion(db: Session, champion_id: int, champ_update: schemas.ChampionUpdate):
    db_champ = get_champion(db, champion_id)
    if not db_champ:
        return None
    for field, value in champ_update:
        pass
    # manual
    if champ_update.nombre is not None:
        db_champ.nombre = champ_update.nombre
    if champ_update.rol is not None:
        db_champ.rol = champ_update.rol
    if champ_update.tasa_victoria is not None:
        db_champ.tasa_victoria = champ_update.tasa_victoria
    if champ_update.tasa_seleccion is not None:
        db_champ.tasa_seleccion = champ_update.tasa_seleccion
    if champ_update.tasa_baneo is not None:
        db_champ.tasa_baneo = champ_update.tasa_baneo
    if champ_update.activo is not None:
        db_champ.activo = champ_update.activo
    db.add(db_champ)
    db.commit()
    db.refresh(db_champ)
    return db_champ

def soft_delete_champion(db: Session, champion_id: int):
    db_champ = get_champion(db, champion_id)
    if not db_champ:
        return None
    db_champ.activo = False
    db.add(db_champ)
    db.commit()
    db.refresh(db_champ)
    return db_champ

# Items
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(nombre=item.nombre, tipo=item.tipo, porcentaje_uso=item.porcentaje_uso)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def list_items(db: Session, skip: int=0, limit:int=100, include_inactive:bool=False):
    q = db.query(models.Item)
    if not include_inactive:
        q = q.filter(models.Item.activo == True)
    return q.offset(skip).limit(limit).all()

def soft_delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db_item.activo = False
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# ChampionItem association
def add_item_to_champion(db: Session, champion_id: int, item_id: int, porcentaje_uso: float = 0.0):
    # avoid duplicates
    exists = db.query(models.ChampionItem).filter(and_(models.ChampionItem.champion_id==champion_id, models.ChampionItem.item_id==item_id)).first()
    if exists:
        exists.porcentaje_uso = porcentaje_uso
        db.add(exists)
        db.commit()
        db.refresh(exists)
        return exists
    assoc = models.ChampionItem(champion_id=champion_id, item_id=item_id, porcentaje_uso=porcentaje_uso)
    db.add(assoc)
    db.commit()
    db.refresh(assoc)
    return assoc

def get_items_for_champion(db: Session, champion_id: int):
    return db.query(models.Item).join(models.ChampionItem, models.Item.id==models.ChampionItem.item_id).filter(models.ChampionItem.champion_id==champion_id).all()

# ChampionVsChampion
def add_cvc(db: Session, cvc: schemas.CVCCreate):
    exists = db.query(models.ChampionVsChampion).filter(and_(models.ChampionVsChampion.champion_id==cvc.champion_id, models.ChampionVsChampion.oponente_id==cvc.oponente_id)).first()
    if exists:
        exists.winrate = cvc.winrate
        db.add(exists)
        db.commit()
        db.refresh(exists)
        return exists
    db_cvc = models.ChampionVsChampion(champion_id=cvc.champion_id, oponente_id=cvc.oponente_id, winrate=cvc.winrate)
    db.add(db_cvc)
    db.commit()
    db.refresh(db_cvc)
    return db_cvc

def get_cvc_by_champion(db: Session, champion_id: int):
    return db.query(models.ChampionVsChampion).filter(models.ChampionVsChampion.champion_id==champion_id).all()
