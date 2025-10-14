"""
Пакет оптимизации производительности для ALADDIN VPN
Включает кэширование соединений, пул соединений и асинхронную обработку
"""

from .connection_cache import ALADDINConnectionCache, ConnectionState, CachedConnection
from .connection_pool import ALADDINConnectionPool, PooledConnection, PoolState
from .async_processor import ALADDINAsyncProcessor, TaskPriority, TaskStatus, AsyncTask
from .performance_manager import ALADDINPerformanceManager, PerformanceMode, PerformanceConfig

__all__ = [
    'ALADDINConnectionCache',
    'ConnectionState',
    'CachedConnection',
    'ALADDINConnectionPool',
    'PooledConnection',
    'PoolState',
    'ALADDINAsyncProcessor',
    'TaskPriority',
    'TaskStatus',
    'AsyncTask',
    'ALADDINPerformanceManager',
    'PerformanceMode',
    'PerformanceConfig'
]
