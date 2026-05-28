import app.models  # noqa: F401
from app.database.db import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
