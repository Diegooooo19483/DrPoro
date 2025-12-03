from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import and_
from typing import List, Optional
from models import Champion

# Champions
def get_champion(db: Session, champion_id: int):
    return db.query(models.Champion).filter(models.Champion.id == champion_id).first()

def get_champion_by_name(db: Session, nombre: str):
    return db.query(models.Champion).filter(models.Champion.nombre == nombre).first()


def list_champions(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False, rol: str = None):
    q = db.query(models.Champion)
    if not include_inactive:
        q = q.filter(models.Champion.activo == True)

    if rol:
        q = q.filter(models.Champion.rol == rol)  # solo campeones de ese rol

    return q.offset(skip).limit(limit).all()


def create_champion(db: Session, champion: schemas.ChampionCreate):
    db_champion = models.Champion(**champion.dict())
    db.add(db_champion)
    db.commit()
    db.refresh(db_champion)
    return db_champion

def update_champion(db: Session, db_champion: models.Champion, champion_update: schemas.ChampionUpdate):
    update_data = champion_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_champion, key, value)

    db.commit()
    db.refresh(db_champion)
    return db_champion


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

def update_item(db: Session, item_id: int, item_data: schemas.ItemUpdate):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        return None

    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

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


#  -------------- NO ENTENDI XD
def get_items_for_champion(db: Session, champion_id: int):
    return db.query(models.Item).join(models.ChampionItem, models.Item.id==models.ChampionItem.item_id).filter(models.ChampionItem.champion_id==champion_id).all()

# 📌 LISTAR TODOS LOS ENFRENTAMIENTOS
def list_cvc(db: Session):
    return db.query(models.ChampionVsChampion).all()


# 📌 CREAR UN NUEVO ENFRENTAMIENTO
def create_cvc(db: Session, champion_id: int, oponente_id: int, winrate: float):
    # Guardar el registro del champion
    cvc = models.ChampionVsChampion(
        champion_id=champion_id,
        oponente_id=oponente_id,
        winrate=winrate
    )
    db.add(cvc)

    # Guardar también el registro invertido para el oponente
    cvc_op = models.ChampionVsChampion(
        champion_id=oponente_id,
        oponente_id=champion_id,
        winrate=100.0 - winrate
    )
    db.add(cvc_op)

    db.commit()
    db.refresh(cvc)
    return cvc

def get_cvc(db: Session, cvc_id: int):
    return db.query(models.ChampionVsChampion).filter(
        models.ChampionVsChampion.id == cvc_id
    ).first()


def update_cvc(db: Session, cvc_id: int, winrate: float):
    registro = get_cvc(db, cvc_id)
    if not registro:
        return None

    registro.winrate = winrate
    db.commit()
    db.refresh(registro)
    return registro


def delete_cvc(db: Session, cvc_id: int):
    registro = get_cvc(db, cvc_id)
    if not registro:
        return None

    db.delete(registro)
    db.commit()
    return True


def list_champions_by_winrate(db: Session, rol: str | None = None):
    q = db.query(models.Champion)
    if rol:
        q = q.filter(models.Champion.rol == rol)
    q = q.order_by(models.Champion.tasa_victoria.desc())
    return q.all()

from sqlalchemy.orm import Session
import models, schemas

# -----------------------------
# USERPROFILE CRUD
# -----------------------------

def create_userprofile(db: Session, profile: schemas.UserProfileCreate):
    # Crear instancia sin los campeones favoritos todavía
    db_profile = models.UserProfile(
        nombre_perfil=profile.nombre_perfil,
        nombre_cuenta=profile.nombre_cuenta,
        region=profile.region,
        foto=profile.foto
    )

    # Agregar campeones favoritos si se pasan IDs
    if profile.campeones_favoritos_ids:
        champions = db.query(models.Champion).filter(
            models.Champion.id.in_(profile.campeones_favoritos_ids)
        ).all()
        db_profile.campeones_favoritos = champions

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_userprofile(db: Session, profile_id: int):
    return db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()

def list_userprofiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserProfile).offset(skip).limit(limit).all()

def update_userprofile(db: Session, profile_id: int, profile_data: schemas.UserProfileCreate):
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        return None

    profile.nombre_perfil = profile_data.nombre_perfil
    profile.nombre_cuenta = profile_data.nombre_cuenta
    profile.region = profile_data.region
    profile.foto = profile_data.foto

    # Actualizar campeones favoritos
    if profile_data.campeones_favoritos_ids is not None:
        champions = db.query(models.Champion).filter(
            models.Champion.id.in_(profile_data.campeones_favoritos_ids)
        ).all()
        profile.campeones_favoritos = champions

    db.commit()
    db.refresh(profile)
    return profile

def delete_userprofile(db: Session, profile_id: int):
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == profile_id).first()
    if not profile:
        return None
    db.delete(profile)
    db.commit()
    return profile
