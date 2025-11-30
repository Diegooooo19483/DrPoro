import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("postgresql://upiybnwgfiqs9yy4oxtf:JaBiK1EK5aLZBXVETk33ORHQkO0ctx@bjkgitbhafdgcvibtsar-postgresql.services.clever-cloud.com:50013/bjkgitbhafdgcvibtsar")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
