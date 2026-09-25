"""SQLAlchemy database engine and session management.

Uses synchronous SQLAlchemy for Phase 1 simplicity. The session factory
is dependency-injected into FastAPI routes.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined by ORM models. Used for dev/testing."""
    Base.metadata.create_all(bind=engine)
