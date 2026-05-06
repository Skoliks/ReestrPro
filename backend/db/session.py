from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from backend.core.config import settings

DATABASE_URL = (
    f"postgresql://{settings.db_user}:"
    f"{settings.db_password}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
)

engine = create_engine(url=DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()