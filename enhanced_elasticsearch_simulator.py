#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Elasticsearch Simulator with SQLite
Улучшенный симулятор Elasticsearch с SQLite для ALADDIN
"""

import sqlite3
import json
import re
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class LogEntry:
    """Запись лога"""
    id: str
    timestamp: datetime
    level: LogLevel
    component: str
    message: str
    metadata: Dict[str, Any]

class EnhancedElasticsearchSimulator:
    """Улучшенный симулятор Elasticsearch с SQLite"""
    
    def __init__(self, db_path: str = "aladdin_logs.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        self.generate_sample_data()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создание таблицы логов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            # Создание индексов для быстрого поиска
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_level ON logs(level)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_component ON logs(component)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_message ON logs(message)
            ''')
            
            conn.commit()
    
    def generate_sample_data(self):
        """Генерация тестовых данных"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, есть ли уже данные
                cursor.execute("SELECT COUNT(*) FROM logs")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return  # Данные уже есть
                
                # Генерируем тестовые данные
                components = [
                    "security_manager", "ai_agent", "threat_detector",
                    "family_monitor", "compliance_checker", "backup_system",
                    "network_scanner", "malware_detector", "user_activity",
                    "system_monitor", "alert_system", "data_processor"
                ]
                
                levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
                
                messages = [
                    "Система безопасности активирована",
                    "Обнаружена подозрительная активность",
                    "Резервное копирование завершено успешно",
                    "Ошибка подключения к внешнему сервису",
                    "Пользователь вошел в систему",
                    "Обновление безопасности установлено",
                    "Сканирование завершено",
                    "Алерт отправлен администратору",
                    "Данные зашифрованы",
                    "Система работает в штатном режиме"
                ]
                
                # Генерируем 1000 записей
                for i in range(1000):
                    timestamp = datetime.now() - timedelta(
                        days=i//100,
                        hours=i%24,
                        minutes=i%60
                    )
                    
                    log_entry = LogEntry(
                        id=f"log_{i}_{int(timestamp.timestamp())}",
                        timestamp=timestamp,
                        level=levels[i % len(levels)],
                        component=components[i % len(components)],
                        message=messages[i % len(messages)],
                        metadata={
                            "user_id": f"user_{i % 50}",
                            "session_id": f"session_{i % 20}",
                            "ip_address": f"192.168.1.{i % 255}",
                            "action": f"action_{i % 10}",
                            "severity": i % 5 + 1
                        }
                    )
                    
                    self._insert_log(cursor, log_entry)
                
                conn.commit()
    
    def _insert_log(self, cursor, log_entry: LogEntry):
        """Вставка записи лога в базу данных"""
        cursor.execute('''
            INSERT OR REPLACE INTO logs 
            (id, timestamp, level, component, message, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            log_entry.id,
            log_entry.timestamp.isoformat(),
            log_entry.level.value,
            log_entry.component,
            log_entry.message,
            json.dumps(log_entry.metadata)
        ))
    
    def add_log(self, level: LogLevel, component: str, message: str, metadata: Dict[str, Any] = None):
        """Добавление нового лога"""
        if metadata is None:
            metadata = {}
        
        log_entry = LogEntry(
            id=f"log_{int(time.time())}_{hash(message) % 10000}",
            timestamp=datetime.now(),
            level=level,
            component=component,
            message=message,
            metadata=metadata
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                self._insert_log(cursor, log_entry)
                conn.commit()
    
    def search(self, query: str = "", level: str = None, component: str = None, 
               start_time: str = None, end_time: str = None, 
               use_regex: bool = False, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Поиск по логам"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Базовый запрос
                sql = "SELECT id, timestamp, level, component, message, metadata FROM logs WHERE 1=1"
                params = []
                
                # Фильтр по уровню
                if level:
                    sql += " AND level = ?"
                    params.append(level)
                
                # Фильтр по компоненту
                if component:
                    sql += " AND component = ?"
                    params.append(component)
                
                # Фильтр по времени
                if start_time:
                    sql += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time:
                    sql += " AND timestamp <= ?"
                    params.append(end_time)
                
                # Поиск по тексту
                if query:
                    if use_regex:
                        try:
                            # Используем REGEXP для SQLite
                            if case_sensitive:
                                sql += " AND (message REGEXP ? OR component REGEXP ? OR metadata REGEXP ?)"
                            else:
                                sql += " AND (LOWER(message) REGEXP LOWER(?) OR LOWER(component) REGEXP LOWER(?) OR LOWER(metadata) REGEXP LOWER(?))"
                            params.extend([query, query, query])
                        except re.error:
                            # Если regex невалидный, используем обычный поиск
                            if case_sensitive:
                                sql += " AND (message LIKE ? OR component LIKE ? OR metadata LIKE ?)"
                            else:
                                sql += " AND (LOWER(message) LIKE LOWER(?) OR LOWER(component) LIKE LOWER(?) OR LOWER(metadata) LIKE LOWER(?))"
                            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
                    else:
                        if case_sensitive:
                            sql += " AND (message LIKE ? OR component LIKE ? OR metadata LIKE ?)"
                        else:
                            sql += " AND (LOWER(message) LIKE LOWER(?) OR LOWER(component) LIKE LOWER(?) OR LOWER(metadata) LIKE LOWER(?))"
                        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
                
                # Сортировка по времени (новые сначала)
                sql += " ORDER BY timestamp DESC LIMIT 1000"
                
                cursor.execute(sql, params)
                results = []
                
                for row in cursor.fetchall():
                    results.append({
                        "id": row[0],
                        "timestamp": row[1],
                        "level": row[2],
                        "component": row[3],
                        "message": row[4],
                        "metadata": json.loads(row[5])
                    })
                
                return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество записей
                cursor.execute("SELECT COUNT(*) FROM logs")
                total_logs = cursor.fetchone()[0]
                
                # Статистика по уровням
                cursor.execute("SELECT level, COUNT(*) FROM logs GROUP BY level")
                level_stats = dict(cursor.fetchall())
                
                # Статистика по компонентам
                cursor.execute("SELECT component, COUNT(*) FROM logs GROUP BY component ORDER BY COUNT(*) DESC LIMIT 10")
                component_stats = dict(cursor.fetchall())
                
                # Последние записи
                cursor.execute("SELECT COUNT(*) FROM logs WHERE timestamp >= datetime('now', '-1 hour')")
                recent_logs = cursor.fetchone()[0]
                
                return {
                    "total_logs": total_logs,
                    "level_stats": level_stats,
                    "component_stats": component_stats,
                    "recent_logs": recent_logs,
                    "database_size": self._get_db_size()
                }
    
    def _get_db_size(self) -> int:
        """Получение размера базы данных"""
        try:
            import os
            return os.path.getsize(self.db_path)
        except:
            return 0
    
    def clear_old_logs(self, days: int = 30):
        """Очистка старых логов"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logs WHERE timestamp < datetime('now', '-{} days')".format(days))
                conn.commit()
                return cursor.rowcount

# Глобальный экземпляр симулятора
es_simulator = EnhancedElasticsearchSimulator()

if __name__ == "__main__":
    # Тестирование симулятора
    print("🧪 Тестирование Enhanced Elasticsearch Simulator...")
    
    # Добавляем тестовый лог
    es_simulator.add_log(
        LogLevel.INFO,
        "test_component",
        "Тестовое сообщение для проверки",
        {"test": True, "value": 42}
    )
    
    # Поиск
    results = es_simulator.search("тест", use_regex=False)
    print(f"📊 Найдено результатов: {len(results)}")
    
    # Статистика
    stats = es_simulator.get_stats()
    print(f"📈 Статистика: {stats}")
    
    print("✅ Тестирование завершено!")