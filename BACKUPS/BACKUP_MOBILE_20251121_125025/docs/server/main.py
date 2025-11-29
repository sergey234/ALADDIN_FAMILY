"""
ALADDIN Backend - FastAPI приложение
Главный файл для запуска API сервера
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import referral
from app.routers import referral_test
from app.routers import payments
from app.database.database import Base, engine

# Создание приложения FastAPI
app = FastAPI(
    title="ALADDIN API",
    version="1.0.0",
    description="Backend API для приложения ALADDIN"
)

# Настройка CORS (разрешить запросы с любых доменов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при запуске (если их нет)
@app.on_event("startup")
async def startup_event():
    """Создание таблиц при запуске приложения"""
    Base.metadata.create_all(bind=engine)

# Подключение роутеров
app.include_router(referral.router, prefix="/api/referral", tags=["referral"])
app.include_router(referral_test.router, tags=["referral-test"])  # Тестовые endpoints
app.include_router(payments.router, tags=["payments"])  # Endpoints для платежей

# Корневой endpoint
@app.get("/")
async def root():
    return {
        "service": "ALADDIN API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

