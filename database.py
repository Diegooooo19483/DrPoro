import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Construimos la URL de la base de datos desde las variables de Clever Cloud
DATABASE_URL = os.getenv(
    "POSTGRESQL_ADDON_URI",
    "sqlite:///./drporo.db"  # fallback local
)

# Reemplazar el puerto si está definido explícitamente
host = os.getenv("POSTGRESQL_ADDON_HOST")
port = os.getenv("POSTGRESQL_ADDON_PORT")
user = os.getenv("POSTGRESQL_ADDON_USER")
password = os.getenv("POSTGRESQL_ADDON_PASSWORD")
db = os.getenv("POSTGRESQL_ADDON_DB")

if host and port and user and password and db:
    DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}?sslmode=require"

# Configuración de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
