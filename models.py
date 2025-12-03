from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

# ============================================================
# 🟨 TABLAS INTERMEDIAS (associative tables)
# ============================================================

# 🔗 Asociación Champion ↔ Item (muchos a muchos)
class ChampionItem(Base):
    __tablename__ = "champion_items"

    id = Column(Integer, primary_key=True, index=True)
    champion_id = Column(Integer, ForeignKey("champions.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    porcentaje_uso = Column(Float, default=0.0)  # % de uso de ese item en ese campeón


# 🔗 Asociación UserProfile ↔ Champion (muchos a muchos)
userprofile_favorite_champions = Table(
    "userprofile_favorite_champions",
    Base.metadata,
    Column("userprofile_id", ForeignKey("userprofiles.id"), primary_key=True),
    Column("champion_id", ForeignKey("champions.id"), primary_key=True)
)

# ============================================================
# 🟥 MODELO PRINCIPAL: Champion
# ============================================================

class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    rol = Column(String, nullable=False)

    tasa_victoria = Column(Float, default=50.0)
    tasa_seleccion = Column(Float, default=0.0)
    tasa_baneo = Column(Float, default=0.0)

    activo = Column(Boolean, default=True)

    # ---------------- RELACIONES ----------------

    # 🔗 Relación con UserProfile (campeones favoritos)
    usuarios_favoritos = relationship(
        "UserProfile",
        secondary=userprofile_favorite_champions,
        back_populates="campeones_favoritos"
    )

    # 🔗 Relación uno-a-uno con Profile (detalles del campeón)
    profile = relationship(
        "Profile",
        back_populates="champion",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # 🔗 Relación con enfrentamientos (ChampionVsChampion)
    enfrentamientos = relationship(
        "ChampionVsChampion",
        back_populates="champion",
        cascade="all, delete-orphan",
        foreign_keys="ChampionVsChampion.champion_id"
    )

    # 🔗 Relación muchos-a-muchos con Item
    items = relationship(
        "Item",
        secondary="champion_items",
        back_populates="champions"
    )

    # 🔗 Relación directa con ChampionItem (tabla intermedia)
    champion_items = relationship(
        "ChampionItem",
        backref="champion",
        cascade="all, delete-orphan"
    )

# ============================================================
# 🟦 MODELO Profile (información extendida del campeón)
# ============================================================

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    champion_id = Column(Integer, ForeignKey("champions.id"), unique=True)
    descripcion = Column(String, default="")
    historia = Column(String, default="")

    champion = relationship("Champion", back_populates="profile")

# ============================================================
# 🟩 MODELO Item
# ============================================================

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    tipo = Column(String, default="")
    porcentaje_uso = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)

    # Relación muchos-a-muchos con Champion
    champions = relationship(
        "Champion",
        secondary="champion_items",
        back_populates="items"
    )

# ============================================================
# 🟥 MODELO Champion vs Champion (matchups)
# ============================================================

class ChampionVsChampion(Base):
    __tablename__ = "champion_vs_champion"

    id = Column(Integer, primary_key=True, index=True)

    champion_id = Column(Integer, ForeignKey("champions.id"), nullable=False)
    oponente_id = Column(Integer, ForeignKey("champions.id"), nullable=False)

    winrate = Column(Float, default=50.0)

    # relaciones
    champion = relationship(
        "Champion",
        foreign_keys=[champion_id],
        back_populates="enfrentamientos"
    )
    oponente = relationship(
        "Champion",
        foreign_keys=[oponente_id]
    )

    # Un campeón no puede tener 2 registros repetidos contra el mismo oponente
    __table_args__ = (
        UniqueConstraint('champion_id', 'oponente_id', name='_champ_opon_uc'),
    )

# ============================================================
# 🟨 MODELO UserProfile
# ============================================================

class UserProfile(Base):
    __tablename__ = "userprofiles"

    id = Column(Integer, primary_key=True, index=True)

    nombre_perfil = Column(String, nullable=False)
    nombre_cuenta = Column(String, nullable=False)
    region = Column(String, nullable=True)
    foto = Column(String, nullable=True)

    # Campeones favoritos (muchos a muchos)
    campeones_favoritos = relationship(
        "Champion",
        secondary=userprofile_favorite_champions,
        back_populates="usuarios_favoritos"
    )

    # Propiedad útil para extraer solo IDs
    @property
    def campeones_favoritos_ids(self):
        return [c.id for c in self.campeones_favoritos]
