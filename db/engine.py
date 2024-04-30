from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker, Session


# export DATABASE_URL="postgresql://somyam:ilovediscord@localhost:5432/discord"
database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", database_url)
engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()