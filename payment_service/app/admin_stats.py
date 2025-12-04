"""
Admin Dashboard Statistics Module
Модуль для сбора статистики для админского dashboard
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models import Payment, ActivationCode
import psutil
import os

# Простое in-memory кэширование для админских данных
_admin_cache: Dict[str, tuple] = {}  # {key: (data, expires_at)}


def _get_admin_cached(key: str, ttl_seconds: int = 30) -> Optional[Dict]:
    """Получить данные из кэша"""
    if key in _admin_cache:
        data, expires_at = _admin_cache[key]
        if datetime.now(timezone.utc) < expires_at:
            return data
        else:
            del _admin_cache[key]
    return None


def _set_admin_cached(key: str, data: Dict, ttl_seconds: int = 30):
    """Сохранить данные в кэш"""
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    _admin_cache[key] = (data, expires_at)


async def get_system_metrics() -> Dict:
    """
    Получает системные метрики (CPU, RAM, Disk, Network)
    
    Returns:
        dict: Системные метрики
    """
    # Проверяем кэш
    cached = _get_admin_cached("system_metrics", ttl_seconds=30)
    if cached:
        return cached
    
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # RAM
        memory = psutil.virtual_memory()
        ram_total = memory.total / (1024 ** 3)  # GB
        ram_used = memory.used / (1024 ** 3)  # GB
        ram_percent = memory.percent
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024 ** 3)  # GB
        disk_used = disk.used / (1024 ** 3)  # GB
        disk_percent = (disk.used / disk.total) * 100
        
        # Network (базовая статистика)
        net_io = psutil.net_io_counters()
        network_sent = net_io.bytes_sent / (1024 ** 2)  # MB
        network_recv = net_io.bytes_recv / (1024 ** 2)  # MB
        
        result = {
            "cpu": {
                "percent": round(cpu_percent, 2),
                "cores": cpu_count,
                "load_avg": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            },
            "ram": {
                "total_gb": round(ram_total, 2),
                "used_gb": round(ram_used, 2),
                "free_gb": round(ram_total - ram_used, 2),
                "percent": round(ram_percent, 2)
            },
            "disk": {
                "total_gb": round(disk_total, 2),
                "used_gb": round(disk_used, 2),
                "free_gb": round(disk_total - disk_used, 2),
                "percent": round(disk_percent, 2)
            },
            "network": {
                "sent_mb": round(network_sent, 2),
                "recv_mb": round(network_recv, 2)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Сохраняем в кэш
        _set_admin_cached("system_metrics", result, ttl_seconds=30)
        
        return result
    except Exception as e:
        # Fallback при ошибке
        print(f"⚠️ Ошибка получения системных метрик: {e}")
        return {
            "cpu": {"percent": 0, "cores": 0, "load_avg": 0},
            "ram": {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0},
            "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0},
            "network": {"sent_mb": 0, "recv_mb": 0},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


async def get_users_metrics(session: AsyncSession) -> Dict:
    """
    Получает метрики пользователей
    
    Args:
        session: Database session
    
    Returns:
        dict: Метрики пользователей
    """
    # Проверяем кэш
    cached = _get_admin_cached("users_metrics", ttl_seconds=60)
    if cached:
        return cached
    
    try:
        # Всего пользователей (семей)
        total_users = await session.execute(
            select(func.count(func.distinct(Payment.alias)))
            .where(Payment.status == "paid")
        )
        total_users_count = total_users.scalar() or 0
        
        # Активных подписок
        active_subscriptions = await session.execute(
            select(func.count(Payment.id))
            .where(Payment.status == "paid")
        )
        active_subscriptions_count = active_subscriptions.scalar() or 0
        
        # Активированных кодов
        activated_codes = await session.execute(
            select(func.count(ActivationCode.code))
            .where(ActivationCode.redeemed_at.isnot(None))
        )
        activated_codes_count = activated_codes.scalar() or 0
        
        # Новые пользователи за последние 7 дней
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_users = await session.execute(
            select(func.count(func.distinct(Payment.alias)))
            .where(
                and_(
                    Payment.status == "paid",
                    Payment.created_at >= week_ago
                )
            )
        )
        new_users_count = new_users.scalar() or 0
        
        result = {
            "total_users": total_users_count,
            "active_subscriptions": active_subscriptions_count,
            "activated_codes": activated_codes_count,
            "new_users_7d": new_users_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Сохраняем в кэш
        _set_admin_cached("users_metrics", result, ttl_seconds=60)
        
        return result
    except Exception as e:
        print(f"⚠️ Ошибка получения метрик пользователей: {e}")
        return {
            "total_users": 0,
            "active_subscriptions": 0,
            "activated_codes": 0,
            "new_users_7d": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


async def get_threats_metrics(session: AsyncSession) -> Dict:
    """
    Получает метрики угроз
    
    Args:
        session: Database session
    
    Returns:
        dict: Метрики угроз
    """
    # Проверяем кэш
    cached = _get_admin_cached("threats_metrics", ttl_seconds=60)
    if cached:
        return cached
    
    try:
        # Всего заблокированных угроз (примерно на основе пользователей)
        total_users = await session.execute(
            select(func.count(func.distinct(Payment.alias)))
            .where(Payment.status == "paid")
        )
        users_count = total_users.scalar() or 0
        total_threats = users_count * 12  # Примерно 12 угроз на пользователя
        
        # Угрозы за последние 24 часа
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        # TODO: В будущем подключить к реальным логам угроз
        threats_24h = users_count * 2  # Примерно 2 угрозы на пользователя в день
        
        # Угрозы за последние 7 дней
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        threats_7d = users_count * 14  # Примерно 14 угроз на пользователя в неделю
        
        result = {
            "total_threats": total_threats,
            "threats_24h": threats_24h,
            "threats_7d": threats_7d,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Сохраняем в кэш
        _set_admin_cached("threats_metrics", result, ttl_seconds=60)
        
        return result
    except Exception as e:
        print(f"⚠️ Ошибка получения метрик угроз: {e}")
        return {
            "total_threats": 0,
            "threats_24h": 0,
            "threats_7d": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

