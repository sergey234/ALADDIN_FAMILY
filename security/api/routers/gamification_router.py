# -*- coding: utf-8 -*-
"""
Gamification API Router - SMART VERSION
-----------------------
Supports automatic userId extraction from JWT if not provided in URL.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path, Depends, Header
from pydantic import BaseModel, Field
import logging
import sys
import os
from jose import jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.database.database import get_db

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
except ImportError:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None

logger = logging.getLogger(__name__)

# JWT Configuration (must match Gateway)
SECRET_KEY = "aladdin-jwt-secret-key-2026-production-ready"
ALGORITHM = "HS256"

async def get_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return "guest_user"
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub", "unknown_user")
    except:
        return "invalid_user"

# Создаем FastAPI Router
router = APIRouter(prefix="/api/gamification", tags=["Gamification"])

# --- Models (совместимые с iOS APIModels.swift) ---

class GamificationBalanceResponse(BaseModel):
    """DTO для баланса единорогов (совместим со Swift GamificationBalanceResponse)."""

    balance: int
    userId: str
    lastModified: datetime
    deviceId: Optional[str] = None
    version: int = 1


class AddBalanceRequest(BaseModel):
    """Запрос изменения баланса (amount может быть как положительным, так и отрицательным)."""

    userId: str
    amount: int
    reason: Optional[str] = None
    deviceId: Optional[str] = None


class GamificationBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None


class AchievementProgressResponse(BaseModel):
    total: int = 0
    unlocked: int = 0
    inProgress: int = 0


class GamificationProgressResponse(BaseModel):
    level: int = 1
    points: int = 0
    nextLevelPoints: int = 100


class GamificationLevelResponse(BaseModel):
    level: int = 1


class RewardResponse(BaseModel):
    """
    Награда в формате, совместимом с iOS `RewardResponse`:
    - rewardId
    - name
    - description
    - price
    - category
    - available
    """

    rewardId: str = Field(..., description="ID награды")
    name: str = Field(..., description="Название награды")
    description: Optional[str] = Field(None, description="Описание награды")
    price: int = Field(..., description="Цена в единорогах", ge=0)
    category: Optional[str] = Field(None, description="Категория награды")
    available: bool = Field(True, description="Доступна ли награда")


class RewardsListResponse(BaseModel):
    """Список наград (совместим со Swift RewardsListResponse)."""

    rewards: List[RewardResponse]
    total: int


class ClaimRewardRequest(BaseModel):
    """Запрос на получение/покупку награды."""

    userId: str
    rewardId: str
    deviceId: Optional[str] = None


class ClaimRewardResponse(BaseModel):
    """Ответ на получение/покупку награды (совместим со Swift ClaimRewardResponse)."""

    success: bool
    newBalance: int
    reward: Optional[RewardResponse] = None
    message: Optional[str] = None


class GamificationSettingsResponse(BaseModel):
    notificationsEnabled: bool = True
    soundsEnabled: bool = True


class TournamentItemResponse(BaseModel):
    id: str
    title: str
    status: str = "upcoming"


def _ensure_gamification_tables(db: Session) -> None:
    """Создаём минимальные таблицы для баланса, если их ещё нет (идемпотентно)."""
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_balance (
                user_id TEXT PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_balance_history (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                balance_after INTEGER NOT NULL,
                reason TEXT,
                device_id TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _get_or_init_balance(db: Session, user_id: str) -> int:
    """Возвращает текущий баланс пользователя, при отсутствии создаёт запись с 0."""
    _ensure_gamification_tables(db)
    row = db.execute(
        text("SELECT balance FROM gamification_balance WHERE user_id = :user_id"),
        {"user_id": user_id},
    ).scalar()
    if row is None:
        db.execute(
            text(
                "INSERT INTO gamification_balance (user_id, balance) VALUES (:user_id, :balance)"
            ),
            {"user_id": user_id, "balance": 0},
        )
        db.commit()
        return 0
    try:
        return int(row)
    except Exception:
        return 0


def _update_balance(
    db: Session,
    user_id: str,
    delta: int,
    reason: Optional[str],
    device_id: Optional[str],
) -> int:
    """
    Применяет изменение баланса и сохраняет историю.
    Положительный delta = начисление, отрицательный = списание.
    """
    _ensure_gamification_tables(db)
    current = _get_or_init_balance(db, user_id)
    new_balance = current + delta
    if new_balance < 0:
        new_balance = 0

    db.execute(
        text(
            """
            UPDATE gamification_balance
            SET balance = :balance, updated_at = NOW()
            WHERE user_id = :user_id
            """
        ),
        {"user_id": user_id, "balance": new_balance},
    )
    db.execute(
        text(
            """
            INSERT INTO gamification_balance_history
                (user_id, amount, balance_after, reason, device_id)
            VALUES (:user_id, :amount, :balance_after, :reason, :device_id)
            """
        ),
        {
            "user_id": user_id,
            "amount": delta,
            "balance_after": new_balance,
            "reason": reason,
            "device_id": device_id,
        },
    )
    db.commit()
    return new_balance


def _ensure_rewards_tables(db: Session) -> None:
    """
    Создаём минимальные таблицы для наград, если их ещё нет (идемпотентно).
    Таблицы:
      - gamification_rewards_catalog (справочник наград)
      - gamification_user_rewards (история полученных наград пользователями)
    """
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_rewards_catalog (
                reward_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL DEFAULT 0,
                category TEXT,
                available BOOLEAN NOT NULL DEFAULT TRUE,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_user_rewards (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                reward_id TEXT NOT NULL,
                source TEXT,
                status TEXT NOT NULL DEFAULT 'claimed',
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.commit()


def _seed_default_rewards_if_empty(db: Session) -> None:
    """Инициализация базового каталога наград, если таблица пуста."""
    _ensure_rewards_tables(db)
    count = db.execute(
        text("SELECT COUNT(*) FROM gamification_rewards_catalog")
    ).scalar() or 0
    if count:
        return

    defaults = [
        {
            "reward_id": "reward_1",
            "name": "Дополнительное время",
            "description": "+30 минут экранного времени",
            "price": 50,
            "category": "time",
            "available": True,
            "sort_order": 1,
        },
        {
            "reward_id": "reward_2",
            "name": "Игра",
            "description": "Разрешение на игру",
            "price": 30,
            "category": "entertainment",
            "available": True,
            "sort_order": 2,
        },
        {
            "reward_id": "shop_1",
            "name": "Игрушка",
            "description": "Крутая игрушка",
            "price": 100,
            "category": "toys",
            "available": True,
            "sort_order": 10,
        },
        {
            "reward_id": "shop_2",
            "name": "Книга",
            "description": "Интересная книга",
            "price": 80,
            "category": "books",
            "available": True,
            "sort_order": 11,
        },
    ]

    for r in defaults:
        db.execute(
            text(
                """
                INSERT INTO gamification_rewards_catalog
                    (reward_id, name, description, price, category, available, sort_order)
                VALUES (:reward_id, :name, :description, :price, :category, :available, :sort_order)
                ON CONFLICT (reward_id) DO NOTHING
                """
            ),
            r,
        )
    db.commit()


def _row_to_reward(row: Dict[str, Any]) -> RewardResponse:
    """Маппинг строки БД в RewardResponse."""
    return RewardResponse(
        rewardId=row["reward_id"],
        name=row["name"],
        description=row.get("description"),
        price=int(row.get("price", 0)),
        category=row.get("category"),
        available=bool(row.get("available", True)),
    )


def _get_rewards_catalog(db: Session) -> List[RewardResponse]:
    """Возвращает весь каталог доступных наград."""
    _seed_default_rewards_if_empty(db)
    rows = (
        db.execute(
            text(
                """
                SELECT reward_id, name, description, price, category, available
                FROM gamification_rewards_catalog
                WHERE available = TRUE
                ORDER BY sort_order, reward_id
                """
            )
        )
        .mappings()
        .all()
    )
    return [_row_to_reward(row) for row in rows]


def _gamification_user_id(userId: Optional[str], current_user: dict) -> str:
    """JWT may expose numeric id — Postgres gamification tables use text user_id."""
    raw = userId or current_user.get("id") or current_user.get("user_id") or current_user.get("sub")
    return str(raw) if raw is not None else "unknown_user"


def _get_user_rewards_history(
    db: Session, user_id: str, limit: int
) -> List[RewardResponse]:
    """История наград пользователя (последние N)."""
    _seed_default_rewards_if_empty(db)
    rows = (
        db.execute(
            text(
                """
                SELECT c.reward_id, c.name, c.description, c.price, c.category, c.available
                FROM gamification_user_rewards ur
                JOIN gamification_rewards_catalog c ON ur.reward_id = c.reward_id
                WHERE ur.user_id = :user_id
                ORDER BY ur.created_at DESC, ur.id DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit},
        )
        .mappings()
        .all()
    )
    return [_row_to_reward(row) for row in rows]


def _get_reward_or_404(db: Session, reward_id: str) -> RewardResponse:
    """Получить награду из каталога или 404."""
    _seed_default_rewards_if_empty(db)
    row = (
        db.execute(
            text(
                """
                SELECT reward_id, name, description, price, category, available
                FROM gamification_rewards_catalog
                WHERE reward_id = :reward_id
                """
            ),
            {"reward_id": reward_id},
        )
        .mappings()
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Reward not found")
    reward = _row_to_reward(row)
    if not reward.available:
        raise HTTPException(status_code=404, detail="Reward is not available")
    return reward


def _register_user_reward(
    db: Session, user_id: str, reward_id: str, source: str, status: str = "claimed"
) -> None:
    """Записываем факт выдачи/покупки награды пользователю."""
    _ensure_rewards_tables(db)
    db.execute(
        text(
            """
            INSERT INTO gamification_user_rewards (user_id, reward_id, source, status)
            VALUES (:user_id, :reward_id, :source, :status)
            """
        ),
        {
            "user_id": user_id,
            "reward_id": reward_id,
            "source": source,
            "status": status,
        },
    )
    db.commit()


def _ensure_achievements_tables(db: Session) -> None:
    """
    Создаём минимальные таблицы для достижений, если их ещё нет (идемпотентно).
    Таблицы:
      - gamification_achievements_catalog (справочник достижений)
      - gamification_user_achievements (прогресс и статус по пользователю)
    """
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_achievements_catalog (
                achievement_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                target INTEGER NOT NULL DEFAULT 1,
                reward INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_user_achievements (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                unlocked BOOLEAN NOT NULL DEFAULT FALSE,
                unlocked_at TIMESTAMP WITHOUT TIME ZONE,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE (user_id, achievement_id)
            )
            """
        )
    )
    db.commit()


def _seed_default_achievements_if_empty(db: Session) -> None:
    """Инициализация базового списка достижений, если таблица пуста."""
    _ensure_achievements_tables(db)
    count = db.execute(
        text("SELECT COUNT(*) FROM gamification_achievements_catalog")
    ).scalar() or 0
    if count:
        return

    defaults = [
        {
            "achievement_id": "ach_1",
            "title": "Первые шаги",
            "description": "Выполните первую задачу",
            "icon": "star",
            "target": 1,
            "reward": 10,
            "sort_order": 1,
        },
        {
            "achievement_id": "ach_5_tasks",
            "title": "Пять заданий",
            "description": "Выполните 5 заданий",
            "icon": "hand.thumbsup",
            "target": 5,
            "reward": 25,
            "sort_order": 2,
        },
    ]

    for a in defaults:
        db.execute(
            text(
                """
                INSERT INTO gamification_achievements_catalog
                    (achievement_id, title, description, icon, target, reward, sort_order)
                VALUES (:achievement_id, :title, :description, :icon, :target, :reward, :sort_order)
                ON CONFLICT (achievement_id) DO NOTHING
                """
            ),
            a,
        )
    db.commit()


class AchievementItemResponse(BaseModel):
    """Краткое DTO достижения для списков и прогресса."""

    id: str
    title: str
    progress: int = 0
    target: int = 1
    unlocked: bool = False


def _get_achievements_for_user(db: Session, user_id: str) -> List[AchievementItemResponse]:
    """
    Возвращает список достижений пользователя в формате AchievementItemResponse.
    """
    _seed_default_achievements_if_empty(db)
    rows = (
        db.execute(
            text(
                """
                SELECT
                    c.achievement_id,
                    c.title,
                    c.target,
                    COALESCE(u.progress, 0) AS progress,
                    COALESCE(u.unlocked, FALSE) AS unlocked
                FROM gamification_achievements_catalog c
                LEFT JOIN gamification_user_achievements u
                    ON u.achievement_id = c.achievement_id AND u.user_id = :user_id
                ORDER BY c.sort_order, c.achievement_id
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .all()
    )

    items: List[AchievementItemResponse] = []
    for row in rows:
        target = int(row.get("target") or 1)
        progress = int(row.get("progress") or 0)
        if progress < 0:
            progress = 0
        if progress > target:
            progress = target
        items.append(
            AchievementItemResponse(
                id=row["achievement_id"],
                title=row["title"],
                progress=progress,
                target=target,
                unlocked=bool(row.get("unlocked", False)),
            )
        )
    return items


def _get_achievements_progress_summary(
    db: Session, user_id: str
) -> AchievementProgressResponse:
    """Считает агрегированный прогресс по достижениям пользователя."""
    items = _get_achievements_for_user(db, user_id)
    total = len(items)
    unlocked = sum(1 for i in items if i.unlocked)
    in_progress = sum(1 for i in items if not i.unlocked and i.progress > 0)
    return AchievementProgressResponse(total=total, unlocked=unlocked, inProgress=in_progress)


def _ensure_settings_tables(db: Session) -> None:
    """
    Таблица настроек геймификации (игровые + уведомления) на пользователя.
    Храним только то, что реально нужно серверу: включены ли уведомления и звуки.
    """
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_settings (
                user_id TEXT PRIMARY KEY,
                notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                sounds_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                achievement_unlocked BOOLEAN NOT NULL DEFAULT TRUE,
                tournament_started BOOLEAN NOT NULL DEFAULT TRUE,
                reward_available BOOLEAN NOT NULL DEFAULT TRUE,
                level_up BOOLEAN NOT NULL DEFAULT TRUE,
                version INTEGER NOT NULL DEFAULT 1,
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _get_or_init_settings_row(db: Session, user_id: str) -> Dict[str, Any]:
    """Возвращает строку настроек пользователя, при отсутствии создаёт с дефолтами."""
    _ensure_settings_tables(db)
    row = (
        db.execute(
            text(
                """
                SELECT *
                FROM gamification_settings
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .first()
    )
    if row:
        return dict(row)

    db.execute(
        text(
            """
            INSERT INTO gamification_settings (
                user_id,
                notifications_enabled,
                sounds_enabled,
                achievement_unlocked,
                tournament_started,
                reward_available,
                level_up,
                version
            ) VALUES (
                :user_id, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 1
            )
            """
        ),
        {"user_id": user_id},
    )
    db.commit()
    return _get_or_init_settings_row(db, user_id)


def _update_settings(
    db: Session,
    user_id: str,
    notifications_enabled: Optional[bool] = None,
    sounds_enabled: Optional[bool] = None,
    achievement_unlocked: Optional[bool] = None,
    tournament_started: Optional[bool] = None,
    reward_available: Optional[bool] = None,
    level_up: Optional[bool] = None,
) -> Dict[str, Any]:
    """Обновляет настройки пользователя (переданные флаги) и возвращает итоговую строку."""
    _ensure_settings_tables(db)
    current = _get_or_init_settings_row(db, user_id)

    payload: Dict[str, Any] = {
        "notifications_enabled": (
            notifications_enabled
            if notifications_enabled is not None
            else current["notifications_enabled"]
        ),
        "sounds_enabled": (
            sounds_enabled if sounds_enabled is not None else current["sounds_enabled"]
        ),
        "achievement_unlocked": (
            achievement_unlocked
            if achievement_unlocked is not None
            else current["achievement_unlocked"]
        ),
        "tournament_started": (
            tournament_started
            if tournament_started is not None
            else current["tournament_started"]
        ),
        "reward_available": (
            reward_available
            if reward_available is not None
            else current["reward_available"]
        ),
        "level_up": level_up if level_up is not None else current["level_up"],
        "version": int(current.get("version", 1)) + 1,
    }

    db.execute(
        text(
            """
            UPDATE gamification_settings
            SET
                notifications_enabled = :notifications_enabled,
                sounds_enabled = :sounds_enabled,
                achievement_unlocked = :achievement_unlocked,
                tournament_started = :tournament_started,
                reward_available = :reward_available,
                level_up = :level_up,
                version = :version,
                updated_at = NOW()
            WHERE user_id = :user_id
            """
        ),
        {"user_id": user_id, **payload},
    )
    db.commit()
    return _get_or_init_settings_row(db, user_id)


def _ensure_progress_table(db: Session) -> None:
    """Таблица агрегированного прогресса геймификации по пользователю."""
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_progress (
                user_id TEXT PRIMARY KEY,
                level INTEGER NOT NULL DEFAULT 1,
                points INTEGER NOT NULL DEFAULT 0,
                next_level_points INTEGER NOT NULL DEFAULT 100,
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _get_or_init_progress(db: Session, user_id: str) -> Dict[str, Any]:
    """Возвращает агрегированный прогресс пользователя или создаёт строку по умолчанию."""
    _ensure_progress_table(db)
    row = (
        db.execute(
            text(
                """
                SELECT user_id, level, points, next_level_points
                FROM gamification_progress
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )
        .mappings()
        .first()
    )
    if row:
        return dict(row)

    db.execute(
        text(
            """
            INSERT INTO gamification_progress (user_id, level, points, next_level_points)
            VALUES (:user_id, 1, 0, 100)
            """
        ),
        {"user_id": user_id},
    )
    db.commit()
    return _get_or_init_progress(db, user_id)


def _update_progress(
    db: Session, user_id: str, delta_points: int
) -> Dict[str, Any]:
    """Добавляет очки к общему прогрессу, повышает уровень по мере необходимости."""
    state = _get_or_init_progress(db, user_id)
    level = int(state["level"])
    points = int(state["points"]) + int(delta_points)
    next_level_points = int(state["next_level_points"])

    if points < 0:
        points = 0

    # Простая схема: каждый уровень требует next_level_points очков,
    # после апгрейда увеличиваем порог на 20%.
    while points >= next_level_points:
        points -= next_level_points
        level += 1
        next_level_points = int(next_level_points * 1.2)
        if next_level_points <= 0:
            next_level_points = 100

    db.execute(
        text(
            """
            UPDATE gamification_progress
            SET level = :level,
                points = :points,
                next_level_points = :next_level_points,
                updated_at = NOW()
            WHERE user_id = :user_id
            """
        ),
        {
            "user_id": user_id,
            "level": level,
            "points": points,
            "next_level_points": next_level_points,
        },
    )
    db.commit()
    return _get_or_init_progress(db, user_id)


def _reset_progress(db: Session, user_id: str) -> None:
    """Сбрасывает прогресс пользователя к уровню 1."""
    _ensure_progress_table(db)
    db.execute(
        text(
            """
            UPDATE gamification_progress
            SET level = 1,
                points = 0,
                next_level_points = 100,
                updated_at = NOW()
            WHERE user_id = :user_id
            """
        ),
        {"user_id": user_id},
    )
    db.commit()


# --- Endpoints ---

@router.get("/balance", response_model=GamificationBalanceResponse)
async def get_gamification_balance_current(
    userId: Optional[str] = Query(None),
    current_user: str = Depends(get_user_from_token),
    db: Session = Depends(get_db),
) -> GamificationBalanceResponse:
    u_id = userId or current_user
    balance = _get_or_init_balance(db, u_id)
    return GamificationBalanceResponse(
        balance=balance,
        userId=u_id,
        lastModified=datetime.now(),
    )

@router.get("/balance/{userId}", response_model=GamificationBalanceResponse)
async def get_gamification_balance(
    userId: str,
    db: Session = Depends(get_db),
) -> GamificationBalanceResponse:
    balance = _get_or_init_balance(db, userId)
    return GamificationBalanceResponse(
        balance=balance,
        userId=userId,
        lastModified=datetime.now(),
    )


@router.post("/balance", response_model=GamificationBalanceResponse)
async def update_gamification_balance_endpoint(
    payload: AddBalanceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> GamificationBalanceResponse:
    """
    POST /api/gamification/balance
    Реальное изменение баланса пользователя.

    - Положительный amount = начисление.
    - Отрицательный amount = списание.
    - userId берём из payload, при отсутствии — из JWT.
    """
    user_id = payload.userId or str(current_user.get("id"))
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    new_balance = _update_balance(
        db=db,
        user_id=user_id,
        delta=payload.amount,
        reason=payload.reason,
        device_id=payload.deviceId,
    )

    return GamificationBalanceResponse(
        balance=new_balance,
        userId=user_id,
        lastModified=datetime.now(),
        deviceId=payload.deviceId,
    )


@router.get("/achievements", response_model=List[AchievementItemResponse])
async def get_gamification_achievements(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AchievementItemResponse]:
    """
    GET /api/gamification/achievements
    Реальный список достижений пользователя (минимальный DTO AchievementItemResponse).
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    items = _get_achievements_for_user(db, str(user_id))
    logger.info("✅ Fetched gamification achievements: user_id=%s total=%d", user_id, len(items))
    return items


@router.get("/achievements/claim", response_model=GamificationBoolResponse)
async def claim_gamification_achievement(
    current_user: dict = Depends(get_current_user),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/achievements/claim
    Compatibility endpoint to avoid wildcard mock fallback on production.
    """
    user_id = current_user.get("id")
    logger.info("✅ Claimed achievement (compat): user_id=%s", user_id)
    return GamificationBoolResponse(success=True, data=True, message="Achievement claimed")


@router.get("/achievements/progress", response_model=AchievementProgressResponse)
async def get_gamification_achievements_progress(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AchievementProgressResponse:
    """
    GET /api/gamification/achievements/progress
    Реальный агрегированный прогресс по достижениям пользователя.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    summary = _get_achievements_progress_summary(db, str(user_id))
    logger.info(
        "✅ Fetched achievements progress: user_id=%s total=%d unlocked=%d inProgress=%d",
        user_id,
        summary.total,
        summary.unlocked,
        summary.inProgress,
    )
    return summary


def _ensure_tournaments_tables(db: Session) -> None:
    """
    Создаём минимальные таблицы для турниров, если их ещё нет (идемпотентно).
    Таблицы:
      - gamification_tournaments_catalog (описание турниров)
      - gamification_user_tournaments (участие пользователя в турнирах)
    """
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_tournaments_catalog (
                tournament_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'upcoming', -- upcoming | active | finished
                prize INTEGER NOT NULL DEFAULT 0,
                max_participants INTEGER,
                start_at TIMESTAMP WITHOUT TIME ZONE,
                end_at TIMESTAMP WITHOUT TIME ZONE,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gamification_user_tournaments (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                tournament_id TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'joined', -- joined | left
                joined_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                left_at TIMESTAMP WITHOUT TIME ZONE,
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE (user_id, tournament_id)
            )
            """
        )
    )
    db.commit()


def _seed_default_tournaments_if_empty(db: Session) -> None:
    """Минимальный набор турниров по умолчанию."""
    _ensure_tournaments_tables(db)
    count = db.execute(
        text("SELECT COUNT(*) FROM gamification_tournaments_catalog")
    ).scalar() or 0
    if count:
        return

    defaults = [
        {
            "tournament_id": "tour_1",
            "title": "Семейный турнир",
            "description": "Кто наберёт больше всего единорогов за неделю",
            "status": "active",
            "prize": 500,
            "max_participants": None,
            "sort_order": 1,
        },
        {
            "tournament_id": "tour_2",
            "title": "Выходные без гаджетов",
            "description": "Марафон цифрового детокса",
            "status": "upcoming",
            "prize": 300,
            "max_participants": None,
            "sort_order": 2,
        },
    ]

    for t in defaults:
        db.execute(
            text(
                """
                INSERT INTO gamification_tournaments_catalog
                    (tournament_id, title, description, status, prize, max_participants, sort_order)
                VALUES (:tournament_id, :title, :description, :status, :prize, :max_participants, :sort_order)
                ON CONFLICT (tournament_id) DO NOTHING
                """
            ),
            t,
        )
    db.commit()


def _get_tournaments(db: Session, status: Optional[str]) -> List[TournamentItemResponse]:
    """Возвращает список турниров (минимальный DTO для списков)."""
    _seed_default_tournaments_if_empty(db)
    if status:
        rows = (
            db.execute(
                text(
                    """
                    SELECT tournament_id, title, status
                    FROM gamification_tournaments_catalog
                    WHERE status = :status
                    ORDER BY sort_order, tournament_id
                    """
                ),
                {"status": status},
            )
            .mappings()
            .all()
        )
    else:
        rows = (
            db.execute(
                text(
                    """
                    SELECT tournament_id, title, status
                    FROM gamification_tournaments_catalog
                    ORDER BY sort_order, tournament_id
                    """
                )
            )
            .mappings()
            .all()
        )
    return [
        TournamentItemResponse(
            id=row["tournament_id"],
            title=row["title"],
            status=row.get("status", "upcoming"),
        )
        for row in rows
    ]


def _get_user_tournaments_history(
    db: Session, user_id: str, limit: int
) -> List[TournamentItemResponse]:
    """История участия пользователя в турнирах (минимальный DTO)."""
    _seed_default_tournaments_if_empty(db)
    rows = (
        db.execute(
            text(
                """
                SELECT
                    c.tournament_id,
                    c.title,
                    c.status
                FROM gamification_user_tournaments ut
                JOIN gamification_tournaments_catalog c
                    ON ut.tournament_id = c.tournament_id
                WHERE ut.user_id = :user_id
                ORDER BY ut.joined_at DESC, ut.id DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit},
        )
        .mappings()
        .all()
    )
    return [
        TournamentItemResponse(
            id=row["tournament_id"],
            title=row["title"],
            status=row.get("status", "upcoming"),
        )
        for row in rows
    ]


def _join_tournament(
    db: Session, user_id: str, tournament_id: str
) -> None:
    """Помечает пользователя как участника турнира."""
    _seed_default_tournaments_if_empty(db)
    _ensure_tournaments_tables(db)
    db.execute(
        text(
            """
            INSERT INTO gamification_user_tournaments (user_id, tournament_id, status)
            VALUES (:user_id, :tournament_id, 'joined')
            ON CONFLICT (user_id, tournament_id)
            DO UPDATE SET status = 'joined', left_at = NULL, updated_at = NOW()
            """
        ),
        {"user_id": user_id, "tournament_id": tournament_id},
    )
    db.commit()


def _leave_tournament(
    db: Session, user_id: str, tournament_id: str
) -> None:
    """Помечает пользователя как покинувшего турнир."""
    _ensure_tournaments_tables(db)
    db.execute(
        text(
            """
            UPDATE gamification_user_tournaments
            SET status = 'left', left_at = NOW(), updated_at = NOW()
            WHERE user_id = :user_id AND tournament_id = :tournament_id
            """
        ),
        {"user_id": user_id, "tournament_id": tournament_id},
    )
    db.commit()


@router.get("/achievements/unlock", response_model=GamificationBoolResponse)
async def unlock_gamification_achievement(
    current_user: dict = Depends(get_current_user),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/achievements/unlock
    Compatibility endpoint to avoid wildcard mock fallback on production.
    """
    user_id = current_user.get("id")
    logger.info("✅ Unlocked achievement (compat): user_id=%s", user_id)
    return GamificationBoolResponse(success=True, data=True, message="Achievement unlocked")


@router.get("/progress", response_model=GamificationProgressResponse)
async def get_gamification_progress(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationProgressResponse:
    """
    GET /api/gamification/progress
    Реальный агрегированный прогресс геймификации пользователя.
    """
    user_id = userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    state = _get_or_init_progress(db, str(user_id))
    logger.info("✅ Fetched gamification progress: user_id=%s level=%s points=%s", user_id, state["level"], state["points"])
    return GamificationProgressResponse(
        level=int(state["level"]),
        points=int(state["points"]),
        nextLevelPoints=int(state["next_level_points"]),
    )


@router.get("/progress/level", response_model=GamificationLevelResponse)
async def get_gamification_progress_level(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationLevelResponse:
    """
    GET /api/gamification/progress/level
    Реальный уровень игрока по агрегированному прогрессу.
    """
    user_id = userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    state = _get_or_init_progress(db, str(user_id))
    level = int(state["level"])
    points = int(state["points"])
    next_level_points = int(state["next_level_points"])
    progress = 0.0
    if next_level_points > 0:
        progress = max(0.0, min(1.0, points / next_level_points))

    logger.info("✅ Fetched gamification level: user_id=%s level=%d progress=%.3f", user_id, level, progress)
    return GamificationLevelResponse(
        level=level,
    )


@router.get("/progress/reset", response_model=GamificationBoolResponse)
async def reset_gamification_progress(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/progress/reset
    Сброс агрегированного прогресса (уровень 1, 0 очков).
    """
    user_id = userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    _reset_progress(db, str(user_id))
    logger.info("✅ Reset gamification progress: user_id=%s", user_id)
    return GamificationBoolResponse(success=True, data=True, message="Progress reset")


@router.get("/progress/stats", response_model=GamificationProgressResponse)
async def get_gamification_progress_stats(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationProgressResponse:
    """
    GET /api/gamification/progress/stats
    Статистика прогресса (сейчас совпадает с агрегированным прогрессом).
    """
    user_id = userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    state = _get_or_init_progress(db, str(user_id))
    logger.info("✅ Fetched gamification progress stats: user_id=%s level=%s points=%s", user_id, state["level"], state["points"])
    return GamificationProgressResponse(
        level=int(state["level"]),
        points=int(state["points"]),
        nextLevelPoints=int(state["next_level_points"]),
    )


@router.get("/progress/update", response_model=GamificationBoolResponse)
async def update_gamification_progress(
    delta: int = Query(10, description="На сколько очков увеличить прогресс", ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/progress/update
    Упрощённое обновление прогресса (увеличивает общие очки на delta).
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    state = _update_progress(db, str(user_id), delta_points=delta)
    logger.info(
        "✅ Updated gamification progress: user_id=%s level=%s points=%s",
        user_id,
        state["level"],
        state["points"],
    )
    return GamificationBoolResponse(success=True, data=True, message="Progress updated")


@router.get("/rewards", response_model=RewardsListResponse)
async def get_gamification_rewards(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RewardsListResponse:
    """
    GET /api/gamification/rewards
    Реальный каталог наград (совместим с iOS RewardsListResponse).
    """
    user_id = userId or current_user.get("id") or "unknown_user"
    rewards = _get_rewards_catalog(db)
    logger.info("✅ Fetched gamification rewards: user_id=%s, count=%d", user_id, len(rewards))
    return RewardsListResponse(rewards=rewards, total=len(rewards))


@router.get("/rewards/history", response_model=List[RewardResponse])
async def get_gamification_rewards_history(
    userId: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[RewardResponse]:
    """
    GET /api/gamification/rewards/history
    История наград пользователя (совместимо с iOS `[RewardResponse]`).
    """
    user_id = _gamification_user_id(userId, current_user)
    history = _get_user_rewards_history(db, user_id, limit)
    logger.info("✅ Fetched gamification rewards history: user_id=%s, count=%d", user_id, len(history))
    return history


@router.get("/rewards/shop", response_model=RewardsListResponse)
async def get_gamification_rewards_shop(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RewardsListResponse:
    """
    GET /api/gamification/rewards/shop
    Магазин наград (каталог доступных товаров).
    """
    user_id = userId or current_user.get("id") or "unknown_user"
    rewards = _get_rewards_catalog(db)
    logger.info("✅ Fetched gamification rewards shop: user_id=%s, count=%d", user_id, len(rewards))
    return RewardsListResponse(rewards=rewards, total=len(rewards))


@router.post("/rewards/claim", response_model=ClaimRewardResponse)
async def claim_gamification_reward(
    request: ClaimRewardRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClaimRewardResponse:
    """
    POST /api/gamification/rewards/claim
    Списание единорогов и выдача награды пользователю.
    """
    user_id = request.userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    reward = _get_reward_or_404(db, request.rewardId)

    current_balance = _get_or_init_balance(db, user_id)
    if current_balance < reward.price:
        raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")

    new_balance = _update_balance(
        db=db,
        user_id=user_id,
        delta=-reward.price,
        reason=f"reward_claim:{reward.rewardId}",
        device_id=request.deviceId,
    )
    _register_user_reward(db, user_id=user_id, reward_id=reward.rewardId, source="claim")

    logger.info(
        "✅ Claimed reward: user_id=%s reward_id=%s price=%d new_balance=%d",
        user_id,
        reward.rewardId,
        reward.price,
        new_balance,
    )
    return ClaimRewardResponse(
        success=True,
        newBalance=new_balance,
        reward=reward,
        message="Награда успешно получена",
    )


@router.post("/rewards/give", response_model=ClaimRewardResponse)
async def give_gamification_reward(
    childId: str = Query(..., description="ID ребёнка, которому выдаём награду"),
    rewardId: str = Query(..., description="ID награды"),
    parentId: Optional[str] = Query(None, description="ID родителя"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClaimRewardResponse:
    """
    POST /api/gamification/rewards/give
    Родитель выдаёт награду ребёнку (баланс можно не изменять).
    """
    _ = current_user.get("id")
    reward = _get_reward_or_404(db, rewardId)

    _register_user_reward(db, user_id=childId, reward_id=reward.rewardId, source="give")

    logger.info(
        "✅ Granted reward: child_id=%s reward_id=%s parent_id=%s",
        childId,
        reward.rewardId,
        parentId,
    )
    return ClaimRewardResponse(
        success=True,
        newBalance=_get_or_init_balance(db, childId),
        reward=reward,
        message="Награда успешно выдана",
    )


@router.post("/rewards/purchase", response_model=ClaimRewardResponse)
async def purchase_gamification_reward(
    request: ClaimRewardRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClaimRewardResponse:
    """
    POST /api/gamification/rewards/purchase
    Покупка награды из магазина (аналогична claim, но с другим source для истории).
    """
    user_id = request.userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    reward = _get_reward_or_404(db, request.rewardId)
    current_balance = _get_or_init_balance(db, user_id)
    if current_balance < reward.price:
        raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")

    new_balance = _update_balance(
        db=db,
        user_id=user_id,
        delta=-reward.price,
        reason=f"reward_purchase:{reward.rewardId}",
        device_id=request.deviceId,
    )
    _register_user_reward(db, user_id=user_id, reward_id=reward.rewardId, source="purchase")

    logger.info(
        "✅ Purchased reward: user_id=%s reward_id=%s price=%d new_balance=%d",
        user_id,
        reward.rewardId,
        reward.price,
        new_balance,
    )
    return ClaimRewardResponse(
        success=True,
        newBalance=new_balance,
        reward=reward,
        message="Товар успешно куплен",
    )


@router.get("/settings", response_model=GamificationSettingsResponse)
async def get_gamification_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationSettingsResponse:
    """
    GET /api/gamification/settings
    Реальные настройки геймификации (упрощённая проекция).
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    row = _get_or_init_settings_row(db, str(user_id))
    logger.info(
        "✅ Fetched gamification settings: user_id=%s notifications=%s sounds=%s",
        user_id,
        row["notifications_enabled"],
        row["sounds_enabled"],
    )
    return GamificationSettingsResponse(
        notificationsEnabled=bool(row["notifications_enabled"]),
        soundsEnabled=bool(row["sounds_enabled"]),
    )


@router.get("/settings/notifications", response_model=GamificationBoolResponse)
async def get_gamification_notifications_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/settings/notifications
    Возвращает текущее состояние флагов уведомлений (сводно).
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    row = _get_or_init_settings_row(db, str(user_id))
    all_enabled = bool(row["achievement_unlocked"]) and bool(row["tournament_started"]) and bool(
        row["reward_available"]
    ) and bool(row["level_up"])
    logger.info("✅ Fetched gamification notification settings: user_id=%s enabled=%s", user_id, all_enabled)
    return GamificationBoolResponse(success=True, data=all_enabled, message="Notifications settings loaded")


@router.get("/settings/notifications/update", response_model=GamificationBoolResponse)
async def update_gamification_notifications_settings(
    achievementUnlocked: Optional[bool] = Query(
        None, description="Уведомления о разблокировке достижений"
    ),
    tournamentStarted: Optional[bool] = Query(
        None, description="Уведомления о начале турнира"
    ),
    rewardAvailable: Optional[bool] = Query(
        None, description="Уведомления о доступных наградах"
    ),
    levelUp: Optional[bool] = Query(None, description="Уведомления о повышении уровня"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/settings/notifications/update
    Обновляет настройки уведомлений (через query-параметры).
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    row = _update_settings(
        db,
        str(user_id),
        achievement_unlocked=achievementUnlocked,
        tournament_started=tournamentStarted,
        reward_available=rewardAvailable,
        level_up=levelUp,
    )
    all_enabled = bool(row["achievement_unlocked"]) and bool(row["tournament_started"]) and bool(
        row["reward_available"]
    ) and bool(row["level_up"])
    logger.info("✅ Updated gamification notification settings: user_id=%s enabled=%s", user_id, all_enabled)
    return GamificationBoolResponse(success=True, data=all_enabled, message="Notifications updated")


@router.get("/settings/update", response_model=GamificationBoolResponse)
async def update_gamification_settings(
    notificationsEnabled: Optional[bool] = Query(
        None, description="Включены ли игровые уведомления"
    ),
    soundsEnabled: Optional[bool] = Query(None, description="Включены ли звуки"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    GET /api/gamification/settings/update
    Обновляет основные игровые настройки (уведомления/звук) через query-параметры.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    row = _update_settings(
        db,
        str(user_id),
        notifications_enabled=notificationsEnabled,
        sounds_enabled=soundsEnabled,
    )
    logger.info(
        "✅ Updated gamification settings: user_id=%s notifications=%s sounds=%s",
        user_id,
        row["notifications_enabled"],
        row["sounds_enabled"],
    )
    return GamificationBoolResponse(success=True, data=True, message="Settings updated")


@router.get("/tournaments", response_model=List[TournamentItemResponse])
async def get_gamification_tournaments(
    status: Optional[str] = Query(None, description="Фильтр по статусу (upcoming, active, finished)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TournamentItemResponse]:
    """
    GET /api/gamification/tournaments
    Реальный список турниров (минимальное DTO TournamentItemResponse).
    """
    user_id = current_user.get("id")
    items = _get_tournaments(db, status=status)
    logger.info(
        "✅ Fetched gamification tournaments: user_id=%s status=%s total=%d",
        user_id,
        status,
        len(items),
    )
    return items


@router.get("/tournaments/history", response_model=List[TournamentItemResponse])
async def get_gamification_tournaments_history(
    userId: Optional[str] = Query(None, description="ID пользователя"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TournamentItemResponse]:
    """
    GET /api/gamification/tournaments/history
    История участия пользователя в турнирах.
    """
    user_id = userId or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    items = _get_user_tournaments_history(db, str(user_id), limit)
    logger.info(
        "✅ Fetched gamification tournaments history: user_id=%s total=%d",
        user_id,
        len(items),
    )
    return items


@router.post("/tournaments/join", response_model=GamificationBoolResponse)
async def join_gamification_tournament(
    tournamentId: str = Query(..., description="ID турнира"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    POST /api/gamification/tournaments/join
    Присоединиться к турниру.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    _join_tournament(db, str(user_id), tournamentId)
    logger.info("✅ Joined gamification tournament: user_id=%s tournament_id=%s", user_id, tournamentId)
    return GamificationBoolResponse(success=True, data=True, message="Tournament joined")


@router.get("/tournaments/leaderboard", response_model=List[TournamentItemResponse])
async def get_gamification_tournaments_leaderboard(
    tournamentId: str = Query(..., description="ID турнира"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TournamentItemResponse]:
    """
    GET /api/gamification/tournaments/leaderboard
    Пока возвращаем просто список участников турнира без реального ранжирования.
    """
    _seed_default_tournaments_if_empty(db)
    _ensure_tournaments_tables(db)
    rows = (
        db.execute(
            text(
                """
                SELECT DISTINCT user_id
                FROM gamification_user_tournaments
                WHERE tournament_id = :tournament_id AND status = 'joined'
                ORDER BY joined_at ASC
                LIMIT :limit
                """
            ),
            {"tournament_id": tournamentId, "limit": limit},
        )
        .mappings()
        .all()
    )
    items = [
        TournamentItemResponse(
            id=tournamentId,
            title=f"participant:{row['user_id']}",
            status="active",
        )
        for row in rows
    ]
    user_id = current_user.get("id")
    logger.info(
        "✅ Fetched tournaments leaderboard: tournament_id=%s requested_by=%s total=%d",
        tournamentId,
        user_id,
        len(items),
    )
    return items


@router.post("/tournaments/leave", response_model=GamificationBoolResponse)
async def leave_gamification_tournament(
    tournamentId: str = Query(..., description="ID турнира"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationBoolResponse:
    """
    POST /api/gamification/tournaments/leave
    Покинуть турнир.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user id missing in token")

    _leave_tournament(db, str(user_id), tournamentId)
    logger.info("✅ Left gamification tournament: user_id=%s tournament_id=%s", user_id, tournamentId)
    return GamificationBoolResponse(success=True, data=True, message="Tournament left")
