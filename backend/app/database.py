from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ===============================
# DATABASE CONFIG
# ===============================
DATABASE_URL = "sqlite:///./chat_app.db"

# ===============================
# ENGINE
# ===============================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite requirement
)

# ===============================
# SESSION
# ===============================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===============================
# BASE MODEL
# ===============================
Base = declarative_base()

# ===============================
# DB DEPENDENCY
# ===============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
