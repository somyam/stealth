from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .base import Base
from .engine import engine
from .models import Channel, Message, User, UserRole, Role, Guild

def setup_database():
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        print(f"An error occurred while creating tables: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    setup_database()