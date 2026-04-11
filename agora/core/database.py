from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from agora.core.config import settings

# SQLite nécessite check_same_thread=False pour FastAPI (threads multiples)
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
