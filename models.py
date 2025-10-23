# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class ChampionItem(Base):
    __tablename__ = "champion_items"
    id = Column(Integer, primary_key=True, index=True)
    champion_id = Column(Integer, ForeignKey("champions.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    porcentaje_uso = Column(Float, default=0.0)


class Champion(Base):
    __tablename__ = "champions"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    rol = Column(String, nullable=False)
    tasa_victoria = Column(Float, default=50.0)
    tasa_seleccion = Column(Float, default=0.0)
    tasa_baneo = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)

    profile = relationship("Profile", back_populates="champion", uselist=False, cascade="all, delete-orphan")

    enfrentamientos = relationship(
        "ChampionVsChampion",
        back_populates="champion",
        cascade="all, delete-orphan",
        foreign_keys="ChampionVsChampion.champion_id"
    )

    items = relationship("Item", secondary="champion_items", back_populates="champions")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    champion_id = Column(Integer, ForeignKey("champions.id"), unique=True)
    descripcion = Column(String, default="")
    historia = Column(String, default="")

    champion = relationship("Champion", back_populates="profile")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    tipo = Column(String, default="")
    porcentaje_uso = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)

    champions = relationship("Champion", secondary="champion_items", back_populates="items")

class ChampionVsChampion(Base):
    __tablename__ = "champion_vs_champion"
    id = Column(Integer, primary_key=True, index=True)
    champion_id = Column(Integer, ForeignKey("champions.id"), nullable=False)
    oponente_id = Column(Integer, ForeignKey("champions.id"), nullable=False)
    winrate = Column(Float, default=50.0)

    champion = relationship("Champion", foreign_keys=[champion_id], back_populates="enfrentamientos")
    oponente = relationship("Champion", foreign_keys=[oponente_id])  # ← agrega esta línea
    __table_args__ = (UniqueConstraint('champion_id', 'oponente_id', name='_champ_opon_uc'),)
