from pathlib import Path
from contextlib import contextmanager
from typing import Generator

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = Path(__file__).resolve().parent / "arc.db"
_ENGINE = sa.create_engine(f"sqlite:///{DB_PATH}", future=True, echo=False)
SessionLocal = sessionmaker(bind=_ENGINE, expire_on_commit=False)

Base = declarative_base()


@contextmanager
def session_scope() -> Generator[sa.orm.Session, None, None]:
    """
    yield a sqlalchemy session inside a transaction.
    commits on success, rolls back on exception.
    """

    session = SessionLocal()
    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
