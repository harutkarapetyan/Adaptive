from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/adaptive"

engine = create_engine(DATABASE_URL,echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def check_connection():
    while True:
        try:
            db = SessionLocal()
            print("Connection successfully")
            db.close()
            break
        except Exception as error:
            print(f"Connection failed: {error}")
            time.sleep(3)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


