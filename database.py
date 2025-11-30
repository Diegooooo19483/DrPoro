from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Clever Cloud te da la URL completa en la variable de entorno
DATABASE_URL = os.getenv("postgresql://ubtfbwjh42jad5ld8zuk:uWkxWmhwyHPgw5xRgdktHNbflQJGAT@bckvhebytlohu0owjmv9-postgresql.services.clever-cloud.com:50013/bckvhebytlohu0owjmv9")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
