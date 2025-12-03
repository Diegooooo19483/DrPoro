from pydantic import BaseModel, Field
from typing import Optional, List

# ============================================================
# 🟦 PROFILE (información extendida del campeón)
# ============================================================

class ProfileBase(BaseModel):
    descripcion: Optional[str] = ""
    historia: Optional[str] = ""

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    champion_id: int

    class Config:
        orm_mode = True


# ============================================================
# 🟩 ITEMS
# ============================================================

class ItemBase(BaseModel):
    nombre: str
    tipo: Optional[str] = ""
    porcentaje_uso: Optional[float] = 0.0

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    nombre: Optional[str]
    tipo: Optional[str]
    porcentaje_uso: Optional[float]

class Item(ItemBase):
    id: int
    activo: bool

    class Config:
        orm_mode = True


# ============================================================
# 🟥 CHAMPIONS
# ============================================================

class ChampionBase(BaseModel):
    nombre: str
    rol: str
    tasa_victoria: float
    tasa_seleccion: float
    tasa_baneo: float
    activo: bool

class ChampionCreate(ChampionBase):
    pass

class ChampionUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None
    tasa_victoria: Optional[float] = None
    tasa_seleccion: Optional[float] = None
    tasa_baneo: Optional[float] = None
    activo: Optional[bool] = None

class Champion(ChampionBase):
    id: int

    class Config:
        from_attributes = True  # usar ORM directamente


# ============================================================
# 🟧 Champion vs Champion (CVC)
# ============================================================

class CVCBase(BaseModel):
    champion_id: int
    oponente_id: int
    winrate: float

class CVCCreate(CVCBase):
    pass

class CVC(CVCBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# 🟨 ChampionItem (relación campeón ↔ items)
# ============================================================

class ChampionItemBase(BaseModel):
    champion_id: int
    item_id: int
    porcentaje_uso: Optional[float] = 0.0

class ChampionItemCreate(ChampionItemBase):
    pass

class ChampionItem(ChampionItemBase):
    id: int

    class Config:
        orm_mode = True


# ============================================================
# 🟦 USER PROFILE
# ============================================================

class UserProfileBase(BaseModel):
    nombre_perfil: str
    nombre_cuenta: str
    region: Optional[str] = None
    foto: Optional[str] = None
    campeones_favoritos_ids: Optional[List[int]] = []

class UserProfileCreate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int

    class Config:
        orm_mode = True
