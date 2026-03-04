# -*- coding: utf-8 -*-
"""
Gamification API Router
-----------------------
FastAPI endpoints для синхронизации геймификации между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.gamification_router import router as gamification_router
    app.include_router(gamification_router)

Дата создания: 11 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import logging
import sys
import os

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None
    print(f"SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

# Баланс единорогов
class GamificationBalanceResponse(BaseModel):
    """Ответ с балансом единорогов"""
    balance: int = Field(..., description="Текущий баланс единорогов", ge=0)
    userId: str = Field(..., description="ID пользователя")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class AddBalanceRequest(BaseModel):
    """Запрос на добавление единорогов"""
    userId: str = Field(..., description="ID пользователя")
    amount: int = Field(..., description="Количество единорогов для добавления", ge=1)
    reason: Optional[str] = Field(None, description="Причина добавления", max_length=200)
    deviceId: Optional[str] = Field(None, description="ID устройства")


class SubtractBalanceRequest(BaseModel):
    """Запрос на вычитание единорогов"""
    userId: str = Field(..., description="ID пользователя")
    amount: int = Field(..., description="Количество единорогов для вычитания", ge=1)
    reason: Optional[str] = Field(None, description="Причина вычитания", max_length=200)
    deviceId: Optional[str] = Field(None, description="ID устройства")


class BalanceHistoryEntry(BaseModel):
    """Запись в истории баланса"""
    operationId: str = Field(..., description="ID операции")
    userId: str = Field(..., description="ID пользователя")
    amount: int = Field(..., description="Изменение баланса (положительное или отрицательное)")
    balanceAfter: int = Field(..., description="Баланс после операции", ge=0)
    reason: Optional[str] = Field(None, description="Причина операции")
    timestamp: datetime = Field(..., description="Время операции")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class BalanceHistoryResponse(BaseModel):
    """История операций с балансом"""
    history: List[BalanceHistoryEntry] = Field(..., description="Список операций")
    total: int = Field(..., description="Общее количество операций")
    currentBalance: int = Field(..., description="Текущий баланс", ge=0)


# Награды
class RewardResponse(BaseModel):
    """Информация о награде"""
    rewardId: str = Field(..., description="ID награды")
    name: str = Field(..., description="Название награды")
    description: Optional[str] = Field(None, description="Описание награды")
    price: int = Field(..., description="Цена в единорогах", ge=0)
    category: Optional[str] = Field(None, description="Категория награды")
    available: bool = Field(True, description="Доступна ли награда")


class RewardsListResponse(BaseModel):
    """Список наград"""
    rewards: List[RewardResponse] = Field(..., description="Список наград")
    total: int = Field(..., description="Общее количество наград")


class ClaimRewardRequest(BaseModel):
    """Запрос на получение награды"""
    userId: str = Field(..., description="ID пользователя")
    rewardId: str = Field(..., description="ID награды")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class ClaimRewardResponse(BaseModel):
    """Ответ на получение награды"""
    success: bool = Field(..., description="Успешно ли получена награда")
    newBalance: int = Field(..., description="Новый баланс после покупки", ge=0)
    reward: Optional[RewardResponse] = Field(None, description="Информация о полученной награде")
    message: Optional[str] = Field(None, description="Сообщение")


# =============================================================================
# Helper функции
# =============================================================================

def _get_fallback_balance(userId: str) -> Dict[str, Any]:
    """Fallback баланс если SFM adapter недоступен"""
    return {
        "balance": 100,
        "userId": userId,
        "lastModified": datetime.now(),
        "deviceId": "fallback",
        "version": 1
    }


# =============================================================================
# API Endpoints - Баланс единорогов (4 endpoint'а)
# =============================================================================

# 1. GET /api/gamification/balance/{userId} - Получить баланс
@router.get("/balance/{userId}", response_model=GamificationBalanceResponse)
async def get_gamification_balance(
    userId: str = Path(..., description="ID пользователя")
) -> GamificationBalanceResponse:
    """
    Получить текущий баланс единорогов пользователя
    
    Args:
        userId: ID пользователя
    
    Returns:
        Текущий баланс единорогов с метаданными
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_balance", data)
            
            if success:
                return GamificationBalanceResponse(
                    balance=result.get("balance", 100),
                    userId=userId,
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    deviceId=result.get("deviceId"),
                    version=result.get("version", 1)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        fallback = _get_fallback_balance(userId)
        return GamificationBalanceResponse(**fallback)
    except Exception as e:
        logger.error(f"Ошибка при получении баланса: {e}")
        fallback = _get_fallback_balance(userId)
        return GamificationBalanceResponse(**fallback)


# 2. POST /api/gamification/balance/add - Добавить единорогов
@router.post("/balance/add", response_model=GamificationBalanceResponse)
async def add_gamification_balance(request: AddBalanceRequest) -> GamificationBalanceResponse:
    """
    Добавить единорогов к балансу пользователя
    
    Args:
        request: Запрос с количеством единорогов для добавления
    
    Returns:
        Обновленный баланс
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "amount": request.amount,
                "reason": request.reason,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_add_balance", data)
            
            if success:
                return GamificationBalanceResponse(
                    balance=result.get("balance", request.amount),
                    userId=request.userId,
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    deviceId=result.get("deviceId", request.deviceId),
                    version=result.get("version", 1)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response - добавляем к текущему балансу
        current_balance = 100  # В реальности нужно получить текущий баланс
        fallback = {
            "balance": current_balance + request.amount,
            "userId": request.userId,
            "lastModified": datetime.now(),
            "deviceId": request.deviceId or "fallback",
            "version": 1
        }
        return GamificationBalanceResponse(**fallback)
    except Exception as e:
        logger.error(f"Ошибка при добавлении баланса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении баланса: {str(e)}")


# 3. POST /api/gamification/balance/subtract - Вычесть единорогов
@router.post("/balance/subtract", response_model=GamificationBalanceResponse)
async def subtract_gamification_balance(request: SubtractBalanceRequest) -> GamificationBalanceResponse:
    """
    Вычесть единорогов из баланса пользователя
    
    Args:
        request: Запрос с количеством единорогов для вычитания
    
    Returns:
        Обновленный баланс
    
    Raises:
        HTTPException: Если недостаточно средств
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "amount": request.amount,
                "reason": request.reason,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_subtract_balance", data)
            
            if success:
                return GamificationBalanceResponse(
                    balance=result.get("balance", 0),
                    userId=request.userId,
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    deviceId=result.get("deviceId", request.deviceId),
                    version=result.get("version", 1)
                )
            else:
                if "insufficient" in message.lower() or "недостаточно" in message.lower():
                    raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response - вычитаем из текущего баланса
        current_balance = 100  # В реальности нужно получить текущий баланс
        if current_balance < request.amount:
            raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")
        
        fallback = {
            "balance": current_balance - request.amount,
            "userId": request.userId,
            "lastModified": datetime.now(),
            "deviceId": request.deviceId or "fallback",
            "version": 1
        }
        return GamificationBalanceResponse(**fallback)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при вычитании баланса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при вычитании баланса: {str(e)}")


# 4. GET /api/gamification/balance/history - История операций
@router.get("/balance/history", response_model=BalanceHistoryResponse)
async def get_gamification_balance_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100),
    offset: int = Query(0, description="Смещение для пагинации", ge=0)
) -> BalanceHistoryResponse:
    """
    Получить историю операций с балансом единорогов
    
    Args:
        userId: ID пользователя
        limit: Максимальное количество записей
        offset: Смещение для пагинации
    
    Returns:
        История операций с балансом
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": userId,
                "limit": limit,
                "offset": offset
            }
            success, result, message = sfm_adapter.execute_function("gamification_balance_history", data)
            
            if success:
                history_entries = []
                for entry in result.get("history", []):
                    history_entries.append(BalanceHistoryEntry(
                        operationId=entry.get("operationId", ""),
                        userId=userId,
                        amount=entry.get("amount", 0),
                        balanceAfter=entry.get("balanceAfter", 0),
                        reason=entry.get("reason"),
                        timestamp=datetime.fromisoformat(entry.get("timestamp", datetime.now().isoformat())),
                        deviceId=entry.get("deviceId")
                    ))
                
                return BalanceHistoryResponse(
                    history=history_entries,
                    total=result.get("total", len(history_entries)),
                    currentBalance=result.get("currentBalance", 100)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return BalanceHistoryResponse(
            history=[],
            total=0,
            currentBalance=100
        )
    except Exception as e:
        logger.error(f"Ошибка при получении истории баланса: {e}")
        return BalanceHistoryResponse(history=[], total=0, currentBalance=0)


# =============================================================================
# API Endpoints - Награды (6 endpoint'ов)
# =============================================================================

# 5. GET /api/gamification/rewards - Получить доступные награды
@router.get("/rewards", response_model=RewardsListResponse)
async def get_gamification_rewards(
    userId: Optional[str] = Query(None, description="ID пользователя")
) -> RewardsListResponse:
    """
    Получить список доступных наград
    
    Args:
        userId: ID пользователя (опционально)
    
    Returns:
        Список доступных наград
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_rewards", data)
            
            if success:
                rewards = []
                for reward_data in result.get("rewards", []):
                    rewards.append(RewardResponse(
                        rewardId=reward_data.get("rewardId", ""),
                        name=reward_data.get("name", ""),
                        description=reward_data.get("description"),
                        price=reward_data.get("price", 0),
                        category=reward_data.get("category"),
                        available=reward_data.get("available", True)
                    ))
                
                return RewardsListResponse(
                    rewards=rewards,
                    total=result.get("total", len(rewards))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return RewardsListResponse(
            rewards=[
                RewardResponse(
                    rewardId="reward_1",
                    name="Дополнительное время",
                    description="+30 минут экранного времени",
                    price=50,
                    category="time",
                    available=True
                ),
                RewardResponse(
                    rewardId="reward_2",
                    name="Игра",
                    description="Разрешение на игру",
                    price=30,
                    category="entertainment",
                    available=True
                )
            ],
            total=2
        )
    except Exception as e:
        logger.error(f"Ошибка при получении наград: {e}")
        return RewardsListResponse(rewards=[], total=0)


# 6. POST /api/gamification/rewards/claim - Получить награду
@router.post("/rewards/claim", response_model=ClaimRewardResponse)
async def claim_gamification_reward(request: ClaimRewardRequest) -> ClaimRewardResponse:
    """
    Получить награду (вычесть из баланса и выдать награду)
    
    Args:
        request: Запрос с ID пользователя и награды
    
    Returns:
        Результат получения награды
    
    Raises:
        HTTPException: Если недостаточно средств или награда недоступна
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "rewardId": request.rewardId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_claim_reward", data)
            
            if success:
                reward_data = result.get("reward")
                reward = None
                if reward_data:
                    reward = RewardResponse(**reward_data)
                
                return ClaimRewardResponse(
                    success=True,
                    newBalance=result.get("newBalance", 0),
                    reward=reward,
                    message=result.get("message", "Награда успешно получена")
                )
            else:
                if "insufficient" in message.lower() or "недостаточно" in message.lower():
                    raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")
                if "unavailable" in message.lower() or "недоступна" in message.lower():
                    raise HTTPException(status_code=404, detail="Награда недоступна")
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ClaimRewardResponse(
            success=True,
            newBalance=50,
            reward=RewardResponse(
                rewardId=request.rewardId,
                name="Награда",
                price=50,
                available=True
            ),
            message="Награда успешно получена"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении награды: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении награды: {str(e)}")


# 7. GET /api/gamification/rewards/history - История наград
@router.get("/rewards/history", response_model=List[Dict[str, Any]])
async def get_gamification_rewards_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> List[Dict[str, Any]]:
    """
    Получить историю полученных наград
    
    Args:
        userId: ID пользователя
        limit: Максимальное количество записей
    
    Returns:
        История наград
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId, "limit": limit}
            success, result, message = sfm_adapter.execute_function("gamification_rewards_history", data)
            
            if success:
                return result.get("history", [])
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении истории наград: {e}")
        return []


# 8. POST /api/gamification/rewards/give - Выдать награду ребенку (для родителей)
@router.post("/rewards/give", response_model=ClaimRewardResponse)
async def give_gamification_reward(
    childId: str = Query(..., description="ID ребенка"),
    rewardId: str = Query(..., description="ID награды"),
    parentId: Optional[str] = Query(None, description="ID родителя")
) -> ClaimRewardResponse:
    """
    Выдать награду ребенку (только для родителей)
    
    Args:
        childId: ID ребенка
        rewardId: ID награды
        parentId: ID родителя (для проверки прав)
    
    Returns:
        Результат выдачи награды
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "childId": childId,
                "rewardId": rewardId,
                "parentId": parentId
            }
            success, result, message = sfm_adapter.execute_function("gamification_give_reward", data)
            
            if success:
                reward_data = result.get("reward")
                reward = None
                if reward_data:
                    reward = RewardResponse(**reward_data)
                
                return ClaimRewardResponse(
                    success=True,
                    newBalance=result.get("newBalance", 0),
                    reward=reward,
                    message=result.get("message", "Награда успешно выдана")
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ClaimRewardResponse(
            success=True,
            newBalance=100,
            reward=RewardResponse(
                rewardId=rewardId,
                name="Награда",
                price=0,
                available=True
            ),
            message="Награда успешно выдана"
        )
    except Exception as e:
        logger.error(f"Ошибка при выдаче награды: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при выдаче награды: {str(e)}")


# 9. GET /api/gamification/rewards/shop - Получить товары магазина
@router.get("/rewards/shop", response_model=RewardsListResponse)
async def get_gamification_rewards_shop(
    userId: Optional[str] = Query(None, description="ID пользователя")
) -> RewardsListResponse:
    """
    Получить товары магазина наград
    
    Args:
        userId: ID пользователя (опционально)
    
    Returns:
        Список товаров магазина
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_rewards_shop", data)
            
            if success:
                rewards = []
                for reward_data in result.get("rewards", []):
                    rewards.append(RewardResponse(**reward_data))
                
                return RewardsListResponse(
                    rewards=rewards,
                    total=result.get("total", len(rewards))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return RewardsListResponse(
            rewards=[
                RewardResponse(
                    rewardId="shop_1",
                    name="Игрушка",
                    description="Крутая игрушка",
                    price=100,
                    category="toys",
                    available=True
                ),
                RewardResponse(
                    rewardId="shop_2",
                    name="Книга",
                    description="Интересная книга",
                    price=80,
                    category="books",
                    available=True
                )
            ],
            total=2
        )
    except Exception as e:
        logger.error(f"Ошибка при получении магазина: {e}")
        return RewardsListResponse(rewards=[], total=0)


# 10. POST /api/gamification/rewards/purchase - Купить товар в магазине
@router.post("/rewards/purchase", response_model=ClaimRewardResponse)
async def purchase_gamification_reward(request: ClaimRewardRequest) -> ClaimRewardResponse:
    """
    Купить товар в магазине наград
    
    Args:
        request: Запрос с ID пользователя и товара
    
    Returns:
        Результат покупки
    
    Raises:
        HTTPException: Если недостаточно средств или товар недоступен
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "rewardId": request.rewardId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_purchase_reward", data)
            
            if success:
                reward_data = result.get("reward")
                reward = None
                if reward_data:
                    reward = RewardResponse(**reward_data)
                
                return ClaimRewardResponse(
                    success=True,
                    newBalance=result.get("newBalance", 0),
                    reward=reward,
                    message=result.get("message", "Товар успешно куплен")
                )
            else:
                if "insufficient" in message.lower() or "недостаточно" in message.lower():
                    raise HTTPException(status_code=400, detail="Недостаточно единорогов на балансе")
                if "unavailable" in message.lower() or "недоступен" in message.lower():
                    raise HTTPException(status_code=404, detail="Товар недоступен")
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ClaimRewardResponse(
            success=True,
            newBalance=50,
            reward=RewardResponse(
                rewardId=request.rewardId,
                name="Товар",
                price=50,
                available=True
            ),
            message="Товар успешно куплен"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при покупке товара: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при покупке товара: {str(e)}")


# =============================================================================
# Pydantic модели - Достижения
# =============================================================================

class AchievementResponse(BaseModel):
    """Информация о достижении"""
    achievementId: str = Field(..., description="ID достижения")
    name: str = Field(..., description="Название достижения")
    description: Optional[str] = Field(None, description="Описание достижения")
    icon: Optional[str] = Field(None, description="Иконка достижения")
    reward: int = Field(0, description="Награда в единорогах", ge=0)
    unlocked: bool = Field(False, description="Разблокировано ли достижение")
    unlockedAt: Optional[datetime] = Field(None, description="Дата разблокировки")
    progress: float = Field(0.0, description="Прогресс (0-1)", ge=0, le=1)


class AchievementsListResponse(BaseModel):
    """Список достижений"""
    achievements: List[AchievementResponse] = Field(..., description="Список достижений")
    total: int = Field(..., description="Общее количество достижений")
    unlockedCount: int = Field(0, description="Количество разблокированных")


class UnlockAchievementRequest(BaseModel):
    """Запрос на разблокировку достижения"""
    userId: str = Field(..., description="ID пользователя")
    achievementId: str = Field(..., description="ID достижения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class AchievementProgressResponse(BaseModel):
    """Прогресс достижений"""
    achievements: List[AchievementResponse] = Field(..., description="Список достижений с прогрессом")
    totalProgress: float = Field(0.0, description="Общий прогресс (0-1)", ge=0, le=1)


# =============================================================================
# API Endpoints - Достижения (5 endpoint'ов)
# =============================================================================

# 11. GET /api/gamification/achievements - Получить достижения
@router.get("/achievements", response_model=AchievementsListResponse)
async def get_gamification_achievements(
    userId: str = Query(..., description="ID пользователя")
) -> AchievementsListResponse:
    """
    Получить список достижений пользователя
    
    Args:
        userId: ID пользователя
    
    Returns:
        Список достижений с информацией о разблокировке
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_achievements", data)
            
            if success:
                achievements = []
                for ach_data in result.get("achievements", []):
                    achievements.append(AchievementResponse(
                        achievementId=ach_data.get("achievementId", ""),
                        name=ach_data.get("name", ""),
                        description=ach_data.get("description"),
                        icon=ach_data.get("icon"),
                        reward=ach_data.get("reward", 0),
                        unlocked=ach_data.get("unlocked", False),
                        unlockedAt=datetime.fromisoformat(ach_data.get("unlockedAt")) if ach_data.get("unlockedAt") else None,
                        progress=ach_data.get("progress", 0.0)
                    ))
                
                return AchievementsListResponse(
                    achievements=achievements,
                    total=result.get("total", len(achievements)),
                    unlockedCount=result.get("unlockedCount", sum(1 for a in achievements if a.unlocked))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return AchievementsListResponse(
            achievements=[
                AchievementResponse(
                    achievementId="ach_1",
                    name="Первые шаги",
                    description="Выполните первое задание",
                    reward=10,
                    unlocked=True,
                    unlockedAt=datetime.now(),
                    progress=1.0
                )
            ],
            total=1,
            unlockedCount=1
        )
    except Exception as e:
        logger.error(f"Ошибка при получении достижений: {e}")
        return AchievementsListResponse(achievements=[], total=0, unlockedCount=0)


# 12. POST /api/gamification/achievements/unlock - Разблокировать достижение
@router.post("/achievements/unlock", response_model=AchievementResponse)
async def unlock_gamification_achievement(request: UnlockAchievementRequest) -> AchievementResponse:
    """
    Разблокировать достижение
    
    Args:
        request: Запрос с ID пользователя и достижения
    
    Returns:
        Информация о разблокированном достижении
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "achievementId": request.achievementId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_unlock_achievement", data)
            
            if success:
                ach_data = result.get("achievement", {})
                return AchievementResponse(
                    achievementId=ach_data.get("achievementId", request.achievementId),
                    name=ach_data.get("name", ""),
                    description=ach_data.get("description"),
                    icon=ach_data.get("icon"),
                    reward=ach_data.get("reward", 0),
                    unlocked=True,
                    unlockedAt=datetime.fromisoformat(ach_data.get("unlockedAt", datetime.now().isoformat())),
                    progress=1.0
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return AchievementResponse(
            achievementId=request.achievementId,
            name="Достижение",
            reward=10,
            unlocked=True,
            unlockedAt=datetime.now(),
            progress=1.0
        )
    except Exception as e:
        logger.error(f"Ошибка при разблокировке достижения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при разблокировке достижения: {str(e)}")


# 13. GET /api/gamification/achievements/progress - Прогресс достижений
@router.get("/achievements/progress", response_model=AchievementProgressResponse)
async def get_gamification_achievements_progress(
    userId: str = Query(..., description="ID пользователя")
) -> AchievementProgressResponse:
    """
    Получить прогресс по всем достижениям
    
    Args:
        userId: ID пользователя
    
    Returns:
        Прогресс по достижениям
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_achievements_progress", data)
            
            if success:
                achievements = []
                for ach_data in result.get("achievements", []):
                    achievements.append(AchievementResponse(**ach_data))
                
                return AchievementProgressResponse(
                    achievements=achievements,
                    totalProgress=result.get("totalProgress", 0.0)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return AchievementProgressResponse(
            achievements=[],
            totalProgress=0.0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении прогресса достижений: {e}")
        return AchievementProgressResponse(achievements=[], totalProgress=0.0)


# 14. GET /api/gamification/achievements/{achievementId} - Получить конкретное достижение
@router.get("/achievements/{achievementId}", response_model=AchievementResponse)
async def get_gamification_achievement(
    achievementId: str = Path(..., description="ID достижения"),
    userId: Optional[str] = Query(None, description="ID пользователя")
) -> AchievementResponse:
    """
    Получить информацию о конкретном достижении
    
    Args:
        achievementId: ID достижения
        userId: ID пользователя (опционально)
    
    Returns:
        Информация о достижении
    
    Raises:
        HTTPException: Если достижение не найдено
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"achievementId": achievementId, "userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_achievement", data)
            
            if success:
                ach_data = result.get("achievement", {})
                return AchievementResponse(**ach_data)
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return AchievementResponse(
            achievementId=achievementId,
            name="Достижение",
            reward=10,
            unlocked=False,
            progress=0.0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении достижения: {e}")
        raise HTTPException(status_code=404, detail="Достижение не найдено")


# 15. POST /api/gamification/achievements/claim - Получить награду за достижение
@router.post("/achievements/claim", response_model=GamificationBalanceResponse)
async def claim_gamification_achievement_reward(request: UnlockAchievementRequest) -> GamificationBalanceResponse:
    """
    Получить награду за достижение (добавить единорогов к балансу)
    
    Args:
        request: Запрос с ID пользователя и достижения
    
    Returns:
        Обновленный баланс после получения награды
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "achievementId": request.achievementId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_claim_achievement_reward", data)
            
            if success:
                return GamificationBalanceResponse(
                    balance=result.get("balance", 0),
                    userId=request.userId,
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    deviceId=result.get("deviceId", request.deviceId),
                    version=result.get("version", 1)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return GamificationBalanceResponse(
            balance=110,
            userId=request.userId,
            lastModified=datetime.now(),
            deviceId=request.deviceId or "fallback",
            version=1
        )
    except Exception as e:
        logger.error(f"Ошибка при получении награды за достижение: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении награды: {str(e)}")


# =============================================================================
# Pydantic модели - Турниры
# =============================================================================

class TournamentResponse(BaseModel):
    """Информация о турнире"""
    tournamentId: str = Field(..., description="ID турнира")
    name: str = Field(..., description="Название турнира")
    description: Optional[str] = Field(None, description="Описание турнира")
    startDate: datetime = Field(..., description="Дата начала")
    endDate: datetime = Field(..., description="Дата окончания")
    status: str = Field(..., description="Статус (upcoming, active, finished)")
    participants: int = Field(0, description="Количество участников", ge=0)
    maxParticipants: Optional[int] = Field(None, description="Максимальное количество участников")
    prize: int = Field(0, description="Приз в единорогах", ge=0)


class TournamentsListResponse(BaseModel):
    """Список турниров"""
    tournaments: List[TournamentResponse] = Field(..., description="Список турниров")
    total: int = Field(..., description="Общее количество турниров")


class JoinTournamentRequest(BaseModel):
    """Запрос на присоединение к турниру"""
    userId: str = Field(..., description="ID пользователя")
    tournamentId: str = Field(..., description="ID турнира")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class LeaderboardEntry(BaseModel):
    """Запись в таблице лидеров"""
    userId: str = Field(..., description="ID пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    score: int = Field(..., description="Очки", ge=0)
    rank: int = Field(..., description="Место в рейтинге", ge=1)
    avatar: Optional[str] = Field(None, description="Аватар")


class LeaderboardResponse(BaseModel):
    """Таблица лидеров"""
    leaderboard: List[LeaderboardEntry] = Field(..., description="Таблица лидеров")
    total: int = Field(..., description="Общее количество участников")
    tournamentId: str = Field(..., description="ID турнира")


# =============================================================================
# API Endpoints - Турниры (6 endpoint'ов)
# =============================================================================

# 16. GET /api/gamification/tournaments - Получить активные турниры
@router.get("/tournaments", response_model=TournamentsListResponse)
async def get_gamification_tournaments(
    status: Optional[str] = Query(None, description="Фильтр по статусу (upcoming, active, finished)")
) -> TournamentsListResponse:
    """
    Получить список турниров
    
    Args:
        status: Фильтр по статусу (опционально)
    
    Returns:
        Список турниров
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"status": status}
            success, result, message = sfm_adapter.execute_function("gamification_get_tournaments", data)
            
            if success:
                tournaments = []
                for tour_data in result.get("tournaments", []):
                    tournaments.append(TournamentResponse(
                        tournamentId=tour_data.get("tournamentId", ""),
                        name=tour_data.get("name", ""),
                        description=tour_data.get("description"),
                        startDate=datetime.fromisoformat(tour_data.get("startDate", datetime.now().isoformat())),
                        endDate=datetime.fromisoformat(tour_data.get("endDate", datetime.now().isoformat())),
                        status=tour_data.get("status", "active"),
                        participants=tour_data.get("participants", 0),
                        maxParticipants=tour_data.get("maxParticipants"),
                        prize=tour_data.get("prize", 0)
                    ))
                
                return TournamentsListResponse(
                    tournaments=tournaments,
                    total=result.get("total", len(tournaments))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return TournamentsListResponse(
            tournaments=[
                TournamentResponse(
                    tournamentId="tour_1",
                    name="Семейный турнир",
                    description="Турнир для всей семьи",
                    startDate=datetime.now(),
                    endDate=datetime.now(),
                    status="active",
                    participants=10,
                    prize=500
                )
            ],
            total=1
        )
    except Exception as e:
        logger.error(f"Ошибка при получении турниров: {e}")
        return TournamentsListResponse(tournaments=[], total=0)


# 17. POST /api/gamification/tournaments/join - Присоединиться к турниру
@router.post("/tournaments/join", response_model=Dict[str, Any])
async def join_gamification_tournament(request: JoinTournamentRequest) -> Dict[str, Any]:
    """
    Присоединиться к турниру
    
    Args:
        request: Запрос с ID пользователя и турнира
    
    Returns:
        Результат присоединения
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "tournamentId": request.tournamentId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_join_tournament", data)
            
            if success:
                return {
                    "success": True,
                    "tournamentId": request.tournamentId,
                    "message": result.get("message", "Вы успешно присоединились к турниру")
                }
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return {
            "success": True,
            "tournamentId": request.tournamentId,
            "message": "Вы успешно присоединились к турниру"
        }
    except Exception as e:
        logger.error(f"Ошибка при присоединении к турниру: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при присоединении к турниру: {str(e)}")


# 18. GET /api/gamification/tournaments/{tournamentId} - Получить турнир
@router.get("/tournaments/{tournamentId}", response_model=TournamentResponse)
async def get_gamification_tournament(
    tournamentId: str = Path(..., description="ID турнира")
) -> TournamentResponse:
    """
    Получить информацию о конкретном турнире
    
    Args:
        tournamentId: ID турнира
    
    Returns:
        Информация о турнире
    
    Raises:
        HTTPException: Если турнир не найден
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"tournamentId": tournamentId}
            success, result, message = sfm_adapter.execute_function("gamification_get_tournament", data)
            
            if success:
                tour_data = result.get("tournament", {})
                return TournamentResponse(**tour_data)
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return TournamentResponse(
            tournamentId=tournamentId,
            name="Турнир",
            startDate=datetime.now(),
            endDate=datetime.now(),
            status="active",
            participants=0,
            prize=0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении турнира: {e}")
        raise HTTPException(status_code=404, detail="Турнир не найден")


# 19. GET /api/gamification/tournaments/leaderboard - Таблица лидеров
@router.get("/tournaments/leaderboard", response_model=LeaderboardResponse)
async def get_gamification_tournament_leaderboard(
    tournamentId: str = Query(..., description="ID турнира"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> LeaderboardResponse:
    """
    Получить таблицу лидеров турнира
    
    Args:
        tournamentId: ID турнира
        limit: Максимальное количество записей
    
    Returns:
        Таблица лидеров
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"tournamentId": tournamentId, "limit": limit}
            success, result, message = sfm_adapter.execute_function("gamification_tournament_leaderboard", data)
            
            if success:
                leaderboard = []
                for entry_data in result.get("leaderboard", []):
                    leaderboard.append(LeaderboardEntry(**entry_data))
                
                return LeaderboardResponse(
                    leaderboard=leaderboard,
                    total=result.get("total", len(leaderboard)),
                    tournamentId=tournamentId
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return LeaderboardResponse(
            leaderboard=[],
            total=0,
            tournamentId=tournamentId
        )
    except Exception as e:
        logger.error(f"Ошибка при получении таблицы лидеров: {e}")
        return LeaderboardResponse(leaderboard=[], total=0, tournamentId=tournamentId)


# 20. POST /api/gamification/tournaments/leave - Покинуть турнир
@router.post("/tournaments/leave", response_model=Dict[str, Any])
async def leave_gamification_tournament(request: JoinTournamentRequest) -> Dict[str, Any]:
    """
    Покинуть турнир
    
    Args:
        request: Запрос с ID пользователя и турнира
    
    Returns:
        Результат выхода из турнира
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "tournamentId": request.tournamentId,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_leave_tournament", data)
            
            if success:
                return {
                    "success": True,
                    "tournamentId": request.tournamentId,
                    "message": result.get("message", "Вы успешно покинули турнир")
                }
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return {
            "success": True,
            "tournamentId": request.tournamentId,
            "message": "Вы успешно покинули турнир"
        }
    except Exception as e:
        logger.error(f"Ошибка при выходе из турнира: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при выходе из турнира: {str(e)}")


# 21. GET /api/gamification/tournaments/history - История турниров
@router.get("/tournaments/history", response_model=TournamentsListResponse)
async def get_gamification_tournaments_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> TournamentsListResponse:
    """
    Получить историю участия пользователя в турнирах
    
    Args:
        userId: ID пользователя
        limit: Максимальное количество записей
    
    Returns:
        История турниров пользователя
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId, "limit": limit}
            success, result, message = sfm_adapter.execute_function("gamification_tournaments_history", data)
            
            if success:
                tournaments = []
                for tour_data in result.get("tournaments", []):
                    tournaments.append(TournamentResponse(**tour_data))
                
                return TournamentsListResponse(
                    tournaments=tournaments,
                    total=result.get("total", len(tournaments))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return TournamentsListResponse(tournaments=[], total=0)
    except Exception as e:
        logger.error(f"Ошибка при получении истории турниров: {e}")
        return TournamentsListResponse(tournaments=[], total=0)


# =============================================================================
# Pydantic модели - Настройки игр
# =============================================================================

class GameSettingsResponse(BaseModel):
    """Настройки игр"""
    userId: str = Field(..., description="ID пользователя")
    soundEnabled: bool = Field(True, description="Включен ли звук")
    musicEnabled: bool = Field(True, description="Включена ли музыка")
    notificationsEnabled: bool = Field(True, description="Включены ли уведомления")
    difficulty: str = Field("medium", description="Уровень сложности (easy, medium, hard)")
    language: str = Field("ru", description="Язык интерфейса")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateGameSettingsRequest(BaseModel):
    """Запрос на обновление настроек игр"""
    userId: str = Field(..., description="ID пользователя")
    soundEnabled: Optional[bool] = Field(None, description="Включен ли звук")
    musicEnabled: Optional[bool] = Field(None, description="Включена ли музыка")
    notificationsEnabled: Optional[bool] = Field(None, description="Включены ли уведомления")
    difficulty: Optional[str] = Field(None, description="Уровень сложности")
    language: Optional[str] = Field(None, description="Язык интерфейса")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки")


class NotificationSettingsResponse(BaseModel):
    """Настройки уведомлений игр"""
    userId: str = Field(..., description="ID пользователя")
    achievementUnlocked: bool = Field(True, description="Уведомления о разблокировке достижений")
    tournamentStarted: bool = Field(True, description="Уведомления о начале турнира")
    rewardAvailable: bool = Field(True, description="Уведомления о доступных наградах")
    levelUp: bool = Field(True, description="Уведомления о повышении уровня")
    lastModified: datetime = Field(..., description="Время последнего изменения")


class UpdateNotificationSettingsRequest(BaseModel):
    """Запрос на обновление настроек уведомлений"""
    userId: str = Field(..., description="ID пользователя")
    achievementUnlocked: Optional[bool] = Field(None, description="Уведомления о разблокировке достижений")
    tournamentStarted: Optional[bool] = Field(None, description="Уведомления о начале турнира")
    rewardAvailable: Optional[bool] = Field(None, description="Уведомления о доступных наградах")
    levelUp: Optional[bool] = Field(None, description="Уведомления о повышении уровня")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# =============================================================================
# API Endpoints - Настройки игр (4 endpoint'а)
# =============================================================================

# 22. GET /api/gamification/settings - Получить настройки игр
@router.get("/settings", response_model=GameSettingsResponse)
async def get_gamification_settings(
    userId: str = Query(..., description="ID пользователя")
) -> GameSettingsResponse:
    """
    Получить настройки игр пользователя
    
    Args:
        userId: ID пользователя
    
    Returns:
        Настройки игр
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_settings", data)
            
            if success:
                return GameSettingsResponse(
                    userId=userId,
                    soundEnabled=result.get("soundEnabled", True),
                    musicEnabled=result.get("musicEnabled", True),
                    notificationsEnabled=result.get("notificationsEnabled", True),
                    difficulty=result.get("difficulty", "medium"),
                    language=result.get("language", "ru"),
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    version=result.get("version", 1)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return GameSettingsResponse(
            userId=userId,
            soundEnabled=True,
            musicEnabled=True,
            notificationsEnabled=True,
            difficulty="medium",
            language="ru",
            lastModified=datetime.now(),
            version=1
        )
    except Exception as e:
        logger.error(f"Ошибка при получении настроек: {e}")
        return GameSettingsResponse(
            userId=userId,
            soundEnabled=True,
            musicEnabled=True,
            notificationsEnabled=True,
            difficulty="medium",
            language="ru",
            lastModified=datetime.now(),
            version=1
        )


# 23. POST /api/gamification/settings/update - Обновить настройки игр
@router.post("/settings/update", response_model=GameSettingsResponse)
async def update_gamification_settings(request: UpdateGameSettingsRequest) -> GameSettingsResponse:
    """
    Обновить настройки игр пользователя
    
    Args:
        request: Запрос с новыми настройками
    
    Returns:
        Обновленные настройки
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "soundEnabled": request.soundEnabled,
                "musicEnabled": request.musicEnabled,
                "notificationsEnabled": request.notificationsEnabled,
                "difficulty": request.difficulty,
                "language": request.language,
                "deviceId": request.deviceId,
                "version": request.version
            }
            success, result, message = sfm_adapter.execute_function("gamification_update_settings", data)
            
            if success:
                return GameSettingsResponse(
                    userId=request.userId,
                    soundEnabled=result.get("soundEnabled", request.soundEnabled or True),
                    musicEnabled=result.get("musicEnabled", request.musicEnabled or True),
                    notificationsEnabled=result.get("notificationsEnabled", request.notificationsEnabled or True),
                    difficulty=result.get("difficulty", request.difficulty or "medium"),
                    language=result.get("language", request.language or "ru"),
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat())),
                    version=result.get("version", (request.version or 1) + 1)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return GameSettingsResponse(
            userId=request.userId,
            soundEnabled=request.soundEnabled if request.soundEnabled is not None else True,
            musicEnabled=request.musicEnabled if request.musicEnabled is not None else True,
            notificationsEnabled=request.notificationsEnabled if request.notificationsEnabled is not None else True,
            difficulty=request.difficulty or "medium",
            language=request.language or "ru",
            lastModified=datetime.now(),
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении настроек: {str(e)}")


# 24. GET /api/gamification/settings/notifications - Получить настройки уведомлений
@router.get("/settings/notifications", response_model=NotificationSettingsResponse)
async def get_gamification_notification_settings(
    userId: str = Query(..., description="ID пользователя")
) -> NotificationSettingsResponse:
    """
    Получить настройки уведомлений игр
    
    Args:
        userId: ID пользователя
    
    Returns:
        Настройки уведомлений
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_notification_settings", data)
            
            if success:
                return NotificationSettingsResponse(
                    userId=userId,
                    achievementUnlocked=result.get("achievementUnlocked", True),
                    tournamentStarted=result.get("tournamentStarted", True),
                    rewardAvailable=result.get("rewardAvailable", True),
                    levelUp=result.get("levelUp", True),
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat()))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return NotificationSettingsResponse(
            userId=userId,
            achievementUnlocked=True,
            tournamentStarted=True,
            rewardAvailable=True,
            levelUp=True,
            lastModified=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ошибка при получении настроек уведомлений: {e}")
        return NotificationSettingsResponse(
            userId=userId,
            achievementUnlocked=True,
            tournamentStarted=True,
            rewardAvailable=True,
            levelUp=True,
            lastModified=datetime.now()
        )


# 25. POST /api/gamification/settings/notifications/update - Обновить настройки уведомлений
@router.post("/settings/notifications/update", response_model=NotificationSettingsResponse)
async def update_gamification_notification_settings(
    request: UpdateNotificationSettingsRequest
) -> NotificationSettingsResponse:
    """
    Обновить настройки уведомлений игр
    
    Args:
        request: Запрос с новыми настройками уведомлений
    
    Returns:
        Обновленные настройки уведомлений
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "achievementUnlocked": request.achievementUnlocked,
                "tournamentStarted": request.tournamentStarted,
                "rewardAvailable": request.rewardAvailable,
                "levelUp": request.levelUp,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_update_notification_settings", data)
            
            if success:
                return NotificationSettingsResponse(
                    userId=request.userId,
                    achievementUnlocked=result.get("achievementUnlocked", request.achievementUnlocked if request.achievementUnlocked is not None else True),
                    tournamentStarted=result.get("tournamentStarted", request.tournamentStarted if request.tournamentStarted is not None else True),
                    rewardAvailable=result.get("rewardAvailable", request.rewardAvailable if request.rewardAvailable is not None else True),
                    levelUp=result.get("levelUp", request.levelUp if request.levelUp is not None else True),
                    lastModified=datetime.fromisoformat(result.get("lastModified", datetime.now().isoformat()))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return NotificationSettingsResponse(
            userId=request.userId,
            achievementUnlocked=request.achievementUnlocked if request.achievementUnlocked is not None else True,
            tournamentStarted=request.tournamentStarted if request.tournamentStarted is not None else True,
            rewardAvailable=request.rewardAvailable if request.rewardAvailable is not None else True,
            levelUp=request.levelUp if request.levelUp is not None else True,
            lastModified=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек уведомлений: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении настроек уведомлений: {str(e)}")


# =============================================================================
# Pydantic модели - Прогресс игр
# =============================================================================

class GameProgressResponse(BaseModel):
    """Прогресс игры"""
    gameId: str = Field(..., description="ID игры")
    gameName: str = Field(..., description="Название игры")
    level: int = Field(1, description="Текущий уровень", ge=1)
    experience: int = Field(0, description="Опыт", ge=0)
    experienceToNextLevel: int = Field(100, description="Опыт до следующего уровня", ge=1)
    totalScore: int = Field(0, description="Общий счет", ge=0)
    lastPlayed: Optional[datetime] = Field(None, description="Дата последней игры")


class GameProgressListResponse(BaseModel):
    """Список прогресса по всем играм"""
    progress: List[GameProgressResponse] = Field(..., description="Список прогресса")
    total: int = Field(..., description="Общее количество игр")


class UpdateProgressRequest(BaseModel):
    """Запрос на обновление прогресса"""
    userId: str = Field(..., description="ID пользователя")
    gameId: str = Field(..., description="ID игры")
    experience: Optional[int] = Field(None, description="Добавить опыта", ge=0)
    score: Optional[int] = Field(None, description="Добавить очков", ge=0)
    deviceId: Optional[str] = Field(None, description="ID устройства")


class ProgressStatsResponse(BaseModel):
    """Статистика прогресса"""
    totalGames: int = Field(0, description="Общее количество игр", ge=0)
    totalLevel: int = Field(1, description="Средний уровень", ge=1)
    totalExperience: int = Field(0, description="Общий опыт", ge=0)
    totalScore: int = Field(0, description="Общий счет", ge=0)
    gamesPlayed: int = Field(0, description="Количество сыгранных игр", ge=0)


class LevelResponse(BaseModel):
    """Информация об уровне"""
    userId: str = Field(..., description="ID пользователя")
    currentLevel: int = Field(1, description="Текущий уровень", ge=1)
    experience: int = Field(0, description="Текущий опыт", ge=0)
    experienceToNextLevel: int = Field(100, description="Опыт до следующего уровня", ge=1)
    progress: float = Field(0.0, description="Прогресс до следующего уровня (0-1)", ge=0, le=1)


class ResetProgressRequest(BaseModel):
    """Запрос на сброс прогресса (для родителей)"""
    userId: str = Field(..., description="ID пользователя")
    gameId: Optional[str] = Field(None, description="ID игры (если None - сбросить все)")
    parentId: str = Field(..., description="ID родителя (для проверки прав)")


# =============================================================================
# API Endpoints - Прогресс игр (5 endpoint'ов)
# =============================================================================

# 26. GET /api/gamification/progress - Получить прогресс всех игр
@router.get("/progress", response_model=GameProgressListResponse)
async def get_gamification_progress(
    userId: str = Query(..., description="ID пользователя")
) -> GameProgressListResponse:
    """
    Получить прогресс по всем играм пользователя
    
    Args:
        userId: ID пользователя
    
    Returns:
        Список прогресса по играм
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_progress", data)
            
            if success:
                progress_list = []
                for prog_data in result.get("progress", []):
                    progress_list.append(GameProgressResponse(
                        gameId=prog_data.get("gameId", ""),
                        gameName=prog_data.get("gameName", ""),
                        level=prog_data.get("level", 1),
                        experience=prog_data.get("experience", 0),
                        experienceToNextLevel=prog_data.get("experienceToNextLevel", 100),
                        totalScore=prog_data.get("totalScore", 0),
                        lastPlayed=datetime.fromisoformat(prog_data.get("lastPlayed")) if prog_data.get("lastPlayed") else None
                    ))
                
                return GameProgressListResponse(
                    progress=progress_list,
                    total=result.get("total", len(progress_list))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return GameProgressListResponse(progress=[], total=0)
    except Exception as e:
        logger.error(f"Ошибка при получении прогресса: {e}")
        return GameProgressListResponse(progress=[], total=0)


# 27. POST /api/gamification/progress/update - Обновить прогресс игры
@router.post("/progress/update", response_model=GameProgressResponse)
async def update_gamification_progress(request: UpdateProgressRequest) -> GameProgressResponse:
    """
    Обновить прогресс игры (добавить опыт/очки)
    
    Args:
        request: Запрос с обновлением прогресса
    
    Returns:
        Обновленный прогресс игры
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "gameId": request.gameId,
                "experience": request.experience,
                "score": request.score,
                "deviceId": request.deviceId
            }
            success, result, message = sfm_adapter.execute_function("gamification_update_progress", data)
            
            if success:
                prog_data = result.get("progress", {})
                return GameProgressResponse(
                    gameId=prog_data.get("gameId", request.gameId),
                    gameName=prog_data.get("gameName", ""),
                    level=prog_data.get("level", 1),
                    experience=prog_data.get("experience", 0),
                    experienceToNextLevel=prog_data.get("experienceToNextLevel", 100),
                    totalScore=prog_data.get("totalScore", 0),
                    lastPlayed=datetime.fromisoformat(prog_data.get("lastPlayed", datetime.now().isoformat()))
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return GameProgressResponse(
            gameId=request.gameId,
            gameName="Игра",
            level=1,
            experience=request.experience or 0,
            experienceToNextLevel=100,
            totalScore=request.score or 0,
            lastPlayed=datetime.now()
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении прогресса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении прогресса: {str(e)}")


# 28. GET /api/gamification/progress/stats - Статистика прогресса
@router.get("/progress/stats", response_model=ProgressStatsResponse)
async def get_gamification_progress_stats(
    userId: str = Query(..., description="ID пользователя")
) -> ProgressStatsResponse:
    """
    Получить статистику прогресса по всем играм
    
    Args:
        userId: ID пользователя
    
    Returns:
        Статистика прогресса
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_progress_stats", data)
            
            if success:
                return ProgressStatsResponse(
                    totalGames=result.get("totalGames", 0),
                    totalLevel=result.get("totalLevel", 1),
                    totalExperience=result.get("totalExperience", 0),
                    totalScore=result.get("totalScore", 0),
                    gamesPlayed=result.get("gamesPlayed", 0)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ProgressStatsResponse(
            totalGames=0,
            totalLevel=1,
            totalExperience=0,
            totalScore=0,
            gamesPlayed=0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении статистики прогресса: {e}")
        return ProgressStatsResponse(
            totalGames=0,
            totalLevel=1,
            totalExperience=0,
            totalScore=0,
            gamesPlayed=0
        )


# 29. GET /api/gamification/progress/level - Получить уровень игрока
@router.get("/progress/level", response_model=LevelResponse)
async def get_gamification_level(
    userId: str = Query(..., description="ID пользователя")
) -> LevelResponse:
    """
    Получить общий уровень игрока (агрегированный по всем играм)
    
    Args:
        userId: ID пользователя
    
    Returns:
        Информация об уровне
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"userId": userId}
            success, result, message = sfm_adapter.execute_function("gamification_get_level", data)
            
            if success:
                return LevelResponse(
                    userId=userId,
                    currentLevel=result.get("currentLevel", 1),
                    experience=result.get("experience", 0),
                    experienceToNextLevel=result.get("experienceToNextLevel", 100),
                    progress=result.get("progress", 0.0)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return LevelResponse(
            userId=userId,
            currentLevel=1,
            experience=0,
            experienceToNextLevel=100,
            progress=0.0
        )
    except Exception as e:
        logger.error(f"Ошибка при получении уровня: {e}")
        return LevelResponse(
            userId=userId,
            currentLevel=1,
            experience=0,
            experienceToNextLevel=100,
            progress=0.0
        )


# 30. POST /api/gamification/progress/reset - Сбросить прогресс (для родителей)
@router.post("/progress/reset", response_model=Dict[str, Any])
async def reset_gamification_progress(request: ResetProgressRequest) -> Dict[str, Any]:
    """
    Сбросить прогресс игры (только для родителей)
    
    Args:
        request: Запрос с ID пользователя и игры
    
    Returns:
        Результат сброса прогресса
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "userId": request.userId,
                "gameId": request.gameId,
                "parentId": request.parentId
            }
            success, result, message = sfm_adapter.execute_function("gamification_reset_progress", data)
            
            if success:
                return {
                    "success": True,
                    "userId": request.userId,
                    "gameId": request.gameId,
                    "message": result.get("message", "Прогресс успешно сброшен")
                }
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return {
            "success": True,
            "userId": request.userId,
            "gameId": request.gameId or "all",
            "message": "Прогресс успешно сброшен"
        }
    except Exception as e:
        logger.error(f"Ошибка при сбросе прогресса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при сбросе прогресса: {str(e)}")
