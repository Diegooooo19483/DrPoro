from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ============================
# URL de la base de datos
# ============================
DATABASE_URL = os.getenv(
    "POSTGRESQL_ADDON_URI",
    "postgresql+psycopg2://unsitmsly62ihl6rgw9j:oknNSa883XU3VvLLfRDXjfhyhyhYQO@b9f912tn9rpz5h895rwc-postgresql.services.clever-cloud.com:50013/b9f912tn9rpz5h895rwc?sslmode=require"
)

# ============================
# Engine
# ============================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# ============================
# Session y Base
# ============================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================
# Inicializar DB
# ============================
def init_db():
    import models
    Base.metadata.create_all(bind=engine)

# ============================
# Dependency
# ============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
