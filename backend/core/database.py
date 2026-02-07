"""
Database Configuration and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from backend.core.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Usage in FastAPI: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create all tables and run auto-migrations"""
    from sqlalchemy import text, inspect
    
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration: ensure new columns exist
    if "sqlite" in settings.database_url:
        with engine.connect() as conn:
            # Check if error_message column exists in protocols table
            result = conn.execute(text("PRAGMA table_info(protocols)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "error_message" not in columns:
                try:
                    conn.execute(text("ALTER TABLE protocols ADD COLUMN error_message TEXT"))
                    conn.commit()
                    print("Auto-migration: Added 'error_message' column to protocols table")
                except Exception as e:
                    print(f"Auto-migration warning: {e}")


def drop_db() -> None:
    """Drop all tables - USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
