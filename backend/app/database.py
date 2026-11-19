"""Kết nối CSDL SQLAlchemy — SQLite mặc định, PostgreSQL-ready."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import DATABASE_URL

# SQLite cần check_same_thread=False để dùng đa luồng với FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency cấp một session DB cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
