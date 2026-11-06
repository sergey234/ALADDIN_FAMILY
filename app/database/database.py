from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import Generator, AsyncGenerator
import os

def _load_backend_dotenv_fallback() -> None:
    # Workers / cron scripts may start without systemd EnvironmentFile (incident 2026-11-06).
    # override=False: values injected by systemd always win.
    from pathlib import Path

    candidates = [
        os.getenv("ALADDIN_BACKEND_ENV_FILE", ""),
        str(Path(__file__).resolve().parents[2] / ".env"),
        "/opt/aladdin-backend/.env",
    ]
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            load_dotenv(candidate, override=False)
            if os.getenv("DATABASE_URL"):
                return


# --- Синхронная часть (PostgreSQL) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    _load_backend_dotenv_fallback()
    DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Асинхронная часть (для компонентов - SQLite) ---
# ВНИМАНИЕ: компоненты сейчас хранятся в payments.db (SQLite)
ASYNC_DATABASE_URL = "sqlite+aiosqlite:////opt/aladdin-backend/payments.db"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
