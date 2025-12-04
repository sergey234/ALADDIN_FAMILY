"""
Dashboard Statistics Module
Модуль для сбора статистики для публичного и приватного dashboard
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models import Payment, ActivationCode

# Простое in-memory кэширование (в будущем заменить на Redis)
_cache: Dict[str, tuple] = {}  # {key: (data, expires_at)}


def _get_cached(key: str, ttl_seconds: int = 60) -> Optional[Dict]:
    """Получить данные из кэша"""
    if key in _cache:
        data, expires_at = _cache[key]
        if datetime.now(timezone.utc) < expires_at:
            return data
        else:
            del _cache[key]
    return None


def _set_cached(key: str, data: Dict, ttl_seconds: int = 60):
    """Сохранить данные в кэш"""
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    _cache[key] = (data, expires_at)


async def get_dashboard_stats(session: AsyncSession, use_cache: bool = True) -> Dict:
    """
    Собирает общую статистику для публичного dashboard
    
    Args:
        session: Database session
        use_cache: Использовать кэш (TTL 60 секунд)
    
    Returns:
        dict: Статистика с полями:
            - protected_devices: количество устройств
            - blocked_threats_total: общее количество заблокированных угроз
            - active_users: количество активных пользователей (семей)
            - uptime_days: дни работы системы
            - threats_timeline: график угроз за 24 часа
            - top_threats: топ-5 угроз
    """
    # Проверяем кэш
    if use_cache:
        cached = _get_cached("dashboard_stats", ttl_seconds=60)
        if cached:
            return cached
    # Получаем количество активных пользователей (семей с оплаченными подписками)
    active_payments = await session.execute(
        select(func.count(func.distinct(Payment.alias)))
        .where(Payment.status == "paid")
    )
    active_users = active_payments.scalar() or 0
    
    # Получаем количество активированных кодов (примерное количество устройств)
    # Каждый активированный код = 1 устройство (упрощенно)
    activated_codes = await session.execute(
        select(func.count(ActivationCode.code))
        .where(ActivationCode.redeemed_at.isnot(None))
    )
    protected_devices = activated_codes.scalar() or 0
    
    # Если нет активированных кодов, используем количество оплаченных платежей * 2 (примерно)
    if protected_devices == 0:
        paid_payments = await session.execute(
            select(func.count(Payment.id))
            .where(Payment.status == "paid")
        )
        paid_count = paid_payments.scalar() or 0
        protected_devices = paid_count * 2  # Примерно 2 устройства на семью
    
    # Получаем количество заблокированных угроз
    # TODO: В будущем подключить к основной БД с логами угроз
    # Пока используем mock данные на основе количества платежей
    blocked_threats_total = active_users * 12  # Примерно 12 угроз на пользователя
    
    # Uptime системы (дни с первого платежа)
    first_payment = await session.execute(
        select(func.min(Payment.created_at))
    )
    first_payment_date = first_payment.scalar()
    
    if first_payment_date:
        if first_payment_date.tzinfo is None:
            first_payment_date = first_payment_date.replace(tzinfo=timezone.utc)
        uptime_days = (datetime.now(timezone.utc) - first_payment_date).days
    else:
        uptime_days = 30  # Fallback
    
    # Генерируем timeline угроз за последние 24 часа
    threats_timeline = await get_threats_timeline(session, hours=24)
    
    # Получаем топ-5 угроз
    top_threats = await get_top_threats(session, limit=5)
    
    result = {
        "protected_devices": protected_devices,
        "blocked_threats_total": blocked_threats_total,
        "active_users": active_users,
        "active_families": active_users,  # Алиас для совместимости
        "uptime_days": uptime_days,
        "threats_timeline": threats_timeline,
        "top_threats": top_threats
    }
    
    # Сохраняем в кэш
    if use_cache:
        _set_cached("dashboard_stats", result, ttl_seconds=60)
    
    return result


async def get_threats_timeline(session: AsyncSession, hours: int = 24) -> List[Dict]:
    """
    Генерирует timeline угроз за указанный период
    
    Args:
        session: Database session
        hours: Количество часов для графика
    
    Returns:
        list: Список точек {timestamp, value}
    """
    # TODO: В будущем подключить к реальным логам угроз
    # Пока генерируем mock данные на основе активности платежей
    
    now = datetime.now(timezone.utc)
    timeline = []
    
    # Генерируем точки каждые 2 часа
    for i in range(hours // 2, -1, -1):
        timestamp = now - timedelta(hours=i * 2)
        
        # Получаем количество платежей за этот период (как индикатор активности)
        period_start = timestamp - timedelta(hours=2)
        period_payments = await session.execute(
            select(func.count(Payment.id))
            .where(
                and_(
                    Payment.created_at >= period_start,
                    Payment.created_at < timestamp
                )
            )
        )
        payment_count = period_payments.scalar() or 0
        
        # Генерируем количество угроз на основе активности
        # Примерно 3-8 угроз на платеж
        threats_count = payment_count * 5 + (i % 3)  # Добавляем вариацию
        
        timeline.append({
            "timestamp": timestamp.isoformat(),
            "value": max(threats_count, 0)  # Минимум 0
        })
    
    return timeline


async def get_top_threats(session: AsyncSession, limit: int = 5) -> List[Dict]:
    """
    Получает топ угроз
    
    Args:
        session: Database session
        limit: Количество угроз
    
    Returns:
        list: Список угроз {name, count, category}
    """
    # TODO: В будущем подключить к реальным данным об угрозах
    # Пока возвращаем mock данные
    
    # Базовые типы угроз на основе статистики
    mock_threats = [
        {"name": "Фишинг", "count": 15, "category": "phishing"},
        {"name": "Мошенничество", "count": 12, "category": "fraud"},
        {"name": "Вредоносное ПО", "count": 8, "category": "malware"},
        {"name": "Подозрительные сайты", "count": 7, "category": "suspicious"},
        {"name": "Небезопасные соединения", "count": 5, "category": "network"}
    ]
    
    # Корректируем количество на основе реальной активности
    active_users = await session.execute(
        select(func.count(func.distinct(Payment.alias)))
        .where(Payment.status == "paid")
    )
    user_count = active_users.scalar() or 1
    
    # Масштабируем данные
    for threat in mock_threats:
        threat["count"] = max(threat["count"] * user_count, threat["count"])
    
    return mock_threats[:limit]


async def get_system_uptime() -> int:
    """
    Получает uptime системы в днях
    
    Returns:
        int: Количество дней работы системы
    """
    # TODO: В будущем получать из системных данных
    # Пока используем фиксированное значение или вычисляем от первого платежа
    return 30  # Fallback

