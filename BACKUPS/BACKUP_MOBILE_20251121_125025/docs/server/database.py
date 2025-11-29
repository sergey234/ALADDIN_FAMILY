"""
Подключение к базе данных PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Параметры подключения к БД
DATABASE_URL = "postgresql://aladdin_user:AladdinSecure2024!@localhost:5432/aladdin_db"

# Создание движка SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=10,
    max_overflow=20
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db() -> Generator:
    """
    Зависимость для получения сессии БД
    Использование:
        @router.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

