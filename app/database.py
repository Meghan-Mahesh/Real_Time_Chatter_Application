from sqlmodel import SQLModel,create_engine, Session
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "project.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL,echo=True)

def create_tables_database():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
