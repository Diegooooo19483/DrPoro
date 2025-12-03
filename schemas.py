from pydantic import BaseModel, Field
from typing import Optional, List

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

from pydantic import BaseModel

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
    nombre: str | None = None
    rol: str | None = None
    tasa_victoria: float | None = None
    tasa_seleccion: float | None = None
    tasa_baneo: float | None = None
    activo: bool | None = None

class Champion(ChampionBase):
    id: int

    class Config:
        from_attributes = True  # ← esto permite usar ORM directamente


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






from pydantic import BaseModel
from typing import List, Optional

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
