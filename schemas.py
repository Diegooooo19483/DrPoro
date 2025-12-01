# schemas.py
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

class Item(ItemBase):
    id: int
    activo: bool
    class Config:
        orm_mode = True

class ChampionBase(BaseModel):
    nombre: str
    rol: str
    tasa_victoria: Optional[float] = 50.0
    tasa_seleccion: Optional[float] = 0.0
    tasa_baneo: Optional[float] = 0.0

class ChampionCreate(ChampionBase):
    profile: Optional[ProfileCreate] = None
    items: List[int] = Field(default_factory=list)

class ChampionUpdate(BaseModel):
    nombre: Optional[str]
    rol: Optional[str]
    tasa_victoria: Optional[float]
    tasa_seleccion: Optional[float]
    tasa_baneo: Optional[float]
    activo: Optional[bool]
    items: List[int] = Field(default_factory=list)
    profile: Optional[ProfileCreate] = None


class Champion(ChampionBase):
    id: int
    activo: bool
    profile: Optional[Profile]
    items: List[Item] = []
    class Config:
        orm_mode = True

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
