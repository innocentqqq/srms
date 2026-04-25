import os
from sqlalchemy import create_engine, MetaData
from app.core.database import SQLALCHEMY_DATABASE_URL

def reset_database():
    print(f"Connecting to {SQLALCHEMY_DATABASE_URL}...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if metadata.sorted_tables:
        print("Dropping existing tables to allow Alembic a fresh start...")
        metadata.drop_all(bind=engine)
        print("All tables dropped successfully.")
    else:
        print("Database is already empty.")

if __name__ == "__main__":
    reset_database()
