# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Database Module
Модуль базы данных для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import ComponentStatus, CoreBase


class DatabaseConnection:
    """Класс для управления соединением с базой данных"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.lock = threading.Lock()

    def connect(self) -> bool:
        """
        Установка соединения с базой данных

        Returns:
            bool: True если соединение установлено
        """
        try:
            with self.lock:
                self.connection = sqlite3.connect(
                    self.db_path, check_same_thread=False, timeout=30.0)
                if self.connection:
                    self.connection.row_factory = sqlite3.Row
                return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        try:
            with self.lock:
                if self.connection:
                    self.connection.close()
                    self.connection = None
        except Exception as e:
            print(f"Ошибка отключения от БД: {e}")

    def execute(self, query: str, params: tuple = ()
                ) -> Optional[sqlite3.Cursor]:
        """
        Выполнение SQL запроса

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            Optional[sqlite3.Cursor]: Курсор с результатами или None
        """
        try:
            with self.lock:
                if not self.connection:
                    if not self.connect():
                        return None

                if self.connection:
                    cursor = self.connection.cursor()
                else:
                    return None
                cursor.execute(query, params)
                return cursor
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def commit(self) -> bool:
        """
        Подтверждение транзакции

        Returns:
            bool: True если транзакция подтверждена
        """
        try:
            with self.lock:
                if self.connection:
                    self.connection.commit()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка подтверждения транзакции: {e}")
            return False

    def rollback(self) -> bool:
        """
        Откат транзакции

        Returns:
            bool: True если транзакция откачена
        """
        try:
            with self.lock:
                if self.connection:
                    self.connection.rollback()
                    return True
                return False
        except Exception as e:
            print(f"Ошибка отката транзакции: {e}")
            return False


class DatabaseManager(CoreBase):
    """Менеджер базы данных для системы ALADDIN"""

    def __init__(self, name: str = "DatabaseManager",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация базы данных
        self.db_path = config.get(
            "db_path", "data/aladdin.db") if config else "data/aladdin.db"
        self.backup_path = config.get(
            "backup_path", "data/backups/") if config else "data/backups/"
        self.max_connections = config.get(
            "max_connections", 10) if config else 10
        self.connection_timeout = config.get(
            "connection_timeout", 30) if config else 30

        # Управление соединениями
        self.connection_pool: List[DatabaseConnection] = []
        self.active_connections = 0
        self.connection_lock = threading.Lock()

        # Статистика
        self.query_count = 0
        self.error_count = 0
        self.last_backup: Optional[datetime] = None

    def initialize(self) -> bool:
        """Инициализация менеджера базы данных"""
        try:
            self.log_activity(
                f"Инициализация менеджера базы данных {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Создание директорий
            self._create_directories()

            # Инициализация базы данных
            if not self._initialize_database():
                raise Exception("Ошибка инициализации базы данных")

            # Создание таблиц
            if not self._create_tables():
                raise Exception("Ошибка создания таблиц")

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер базы данных {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера базы данных {self.name}: {e}",
                "error")
            return False

    def _create_directories(self):
        """Создание необходимых директорий"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            Path(self.backup_path).mkdir(parents=True, exist_ok=True)
            self.log_activity("Директории для базы данных созданы")
        except Exception as e:
            self.log_activity(f"Ошибка создания директорий: {e}", "error")

    def _initialize_database(self) -> bool:
        """Инициализация базы данных"""
        try:
            # Создание основного соединения
            connection = DatabaseConnection(self.db_path)
            if not connection.connect():
                return False

            self.connection_pool.append(connection)
            self.active_connections = 1

            self.log_activity("База данных инициализирована")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации базы данных: {e}", "error")
            return False

    def _create_tables(self) -> bool:
        """Создание таблиц базы данных"""
        try:
            tables = [
                # Таблица пользователей
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    security_level TEXT DEFAULT 'medium'
                )
                """,
                # Таблица событий безопасности
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0,
                    resolution_time TIMESTAMP,
                    event_data TEXT
                )
                """,
                # Таблица угроз
                """
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_type TEXT NOT NULL,
                    threat_name TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    threat_data TEXT
                )
                """,
                # Таблица аудита
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    user_id INTEGER,
                    resource TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    details TEXT
                )
                """,
                # Таблица конфигураций
                """
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                # Таблица метрик
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    component TEXT,
                    tags TEXT
                )
                """,
            ]

            connection = self.get_connection()
            if not connection:
                return False

            for table_sql in tables:
                cursor = connection.execute(table_sql)
                if not cursor:
                    return False

            connection.commit()
            self.log_activity("Таблицы базы данных созданы")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка создания таблиц: {e}", "error")
            return False

    def get_connection(self) -> Optional[DatabaseConnection]:
        """
        Получение соединения с базой данных

        Returns:
            Optional[DatabaseConnection]: Соединение с БД или None
        """
        try:
            with self.connection_lock:
                if self.connection_pool:
                    return self.connection_pool[0]  # Простая реализация
                else:
                    connection = DatabaseConnection(self.db_path)
                    if connection.connect():
                        self.connection_pool.append(connection)
                        self.active_connections += 1
                        return connection
                    return None
        except Exception as e:
            self.log_activity(f"Ошибка получения соединения: {e}", "error")
            return None

    def execute_query(self, query: str, params: tuple = ()
                      ) -> Optional[List[Dict[str, Any]]]:
        """
        Выполнение запроса к базе данных

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            Optional[List[Dict[str, Any]]]: Результаты запроса или None
        """
        try:
            connection = self.get_connection()
            if not connection:
                return None

            cursor = connection.execute(query, params)
            if not cursor:
                return None

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))

            self.query_count += 1
            return results

        except Exception as e:
            self.error_count += 1
            self.log_activity(f"Ошибка выполнения запроса: {e}", "error")
            return None

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        Выполнение обновления базы данных

        Args:
            query: SQL запрос
            params: Параметры запроса

        Returns:
            bool: True если обновление выполнено успешно
        """
        try:
            connection = self.get_connection()
            if not connection:
                return False

            cursor = connection.execute(query, params)
            if not cursor:
                return False

            success = connection.commit()
            if success:
                self.query_count += 1

            return success

        except Exception as e:
            self.error_count += 1
            self.log_activity(f"Ошибка выполнения обновления: {e}", "error")
            return False

    def insert_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        security_level: str = "medium",
    ) -> bool:
        """
        Добавление пользователя

        Args:
            username: Имя пользователя
            email: Email пользователя
            password_hash: Хеш пароля
            security_level: Уровень безопасности

        Returns:
            bool: True если пользователь добавлен
        """
        query = """
        INSERT INTO users (username, email, password_hash, security_level)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_update(
            query, (username, email, password_hash, security_level))

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по имени

        Args:
            username: Имя пользователя

        Returns:
            Optional[Dict[str, Any]]: Данные пользователя или None
        """
        query = "SELECT * FROM users WHERE username = ?"
        results = self.execute_query(query, (username,))
        return results[0] if results else None

    def add_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Добавление события безопасности

        Args:
            event_type: Тип события
            severity: Серьезность события
            description: Описание события
            source: Источник события
            event_data: Дополнительные данные события

        Returns:
            bool: True если событие добавлено
        """
        query = """
        INSERT INTO security_events
        (event_type, severity, description, source, event_data)
        VALUES (?, ?, ?, ?, ?)
        """
        event_data_json = json.dumps(event_data) if event_data else None
        return self.execute_update(
            query, (event_type, severity, description, source, event_data_json))

    def get_security_events(
            self, limit: int = 100, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Получение событий безопасности

        Args:
            limit: Максимальное количество событий
            resolved: Фильтр по статусу разрешения

        Returns:
            List[Dict[str, Any]]: Список событий
        """
        if resolved is not None:
            query = "SELECT * FROM security_events WHERE resolved = ? " "ORDER BY timestamp DESC LIMIT ?"
            return self.execute_query(query, (resolved, limit)) or []
        else:
            query = "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?"
            return self.execute_query(query, (limit,)) or []

    def add_threat(
        self,
        threat_type: str,
        threat_name: str,
        description: str,
        severity: str,
        confidence: float = 0.5,
        threat_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Добавление угрозы

        Args:
            threat_type: Тип угрозы
            threat_name: Название угрозы
            description: Описание угрозы
            severity: Серьезность угрозы
            confidence: Уверенность в обнаружении
            threat_data: Дополнительные данные угрозы

        Returns:
            bool: True если угроза добавлена
        """
        query = """
        INSERT INTO threats
        (threat_type, threat_name, description, severity, confidence, threat_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        threat_data_json = json.dumps(threat_data) if threat_data else None
        return self.execute_update(
            query,
            (
                threat_type,
                threat_name,
                description,
                severity,
                confidence,
                threat_data_json,
            ),
        )

    def get_active_threats(self) -> List[Dict[str, Any]]:
        """
        Получение активных угроз

        Returns:
            List[Dict[str, Any]]: Список активных угроз
        """
        query = "SELECT * FROM threats WHERE status = 'active' ORDER BY detected_at DESC"
        return self.execute_query(query) or []

    def add_audit_log(
        self,
        action: str,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Добавление записи в аудиторский журнал

        Args:
            action: Действие
            user_id: ID пользователя
            resource: Ресурс
            ip_address: IP адрес
            user_agent: User Agent
            details: Дополнительные детали

        Returns:
            bool: True если запись добавлена
        """
        query = """
        INSERT INTO audit_log
        (action, user_id, resource, ip_address, user_agent, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        details_json = json.dumps(details) if details else None
        return self.execute_update(
            query,
            (action,
             user_id,
             resource,
             ip_address,
             user_agent,
             details_json))

    def get_audit_log(self, limit: int = 100,
                      user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получение аудиторского журнала

        Args:
            limit: Максимальное количество записей
            user_id: Фильтр по пользователю

        Returns:
            List[Dict[str, Any]]: Список записей аудита
        """
        if user_id:
            query = "SELECT * FROM audit_log WHERE user_id = ? " "ORDER BY timestamp DESC LIMIT ?"
            return self.execute_query(query, (user_id, limit)) or []
        else:
            query = "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?"
            return self.execute_query(query, (limit,)) or []

    def set_configuration(
            self,
            key: str,
            value: str,
            config_type: str = "string",
            description: Optional[str] = None) -> bool:
        """
        Установка конфигурации

        Args:
            key: Ключ конфигурации
            value: Значение конфигурации
            config_type: Тип конфигурации
            description: Описание конфигурации

        Returns:
            bool: True если конфигурация установлена
        """
        query = """
        INSERT OR REPLACE INTO configurations
        (config_key, config_value, config_type, description, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        return self.execute_update(
            query, (key, value, config_type, description))

    def get_configuration(self, key: str) -> Optional[str]:
        """
        Получение конфигурации

        Args:
            key: Ключ конфигурации

        Returns:
            Optional[str]: Значение конфигурации или None
        """
        query = "SELECT config_value FROM configurations WHERE config_key = ?"
        results = self.execute_query(query, (key,))
        return results[0]["config_value"] if results else None

    def add_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        component: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Добавление метрики

        Args:
            metric_name: Название метрики
            metric_value: Значение метрики
            metric_unit: Единица измерения
            component: Компонент
            tags: Теги метрики

        Returns:
            bool: True если метрика добавлена
        """
        query = """
        INSERT INTO metrics
        (metric_name, metric_value, metric_unit, component, tags)
        VALUES (?, ?, ?, ?, ?)
        """
        tags_json = json.dumps(tags) if tags else None
        return self.execute_update(
            query,
            (metric_name,
             metric_value,
             metric_unit,
             component,
             tags_json))

    def get_metrics(self,
                    metric_name: Optional[str] = None,
                    component: Optional[str] = None,
                    hours: int = 24) -> List[Dict[str,
                                                  Any]]:
        """
        Получение метрик

        Args:
            metric_name: Название метрики
            component: Компонент
            hours: Количество часов для выборки

        Returns:
            List[Dict[str, Any]]: Список метрик
        """
        if metric_name and component:
            query = """
            SELECT * FROM metrics
            WHERE metric_name = ? AND component = ? AND
                  timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            """.format(
                hours
            )
            return self.execute_query(query, (metric_name, component)) or []
        elif metric_name:
            query = """
            SELECT * FROM metrics
            WHERE metric_name = ? AND timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            """.format(
                hours
            )
            return self.execute_query(query, (metric_name,)) or []
        else:
            query = """
            SELECT * FROM metrics
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            """.format(
                hours
            )
            return self.execute_query(query) or []

    def create_backup(self) -> bool:
        """
        Создание резервной копии базы данных

        Returns:
            bool: True если резервная копия создана
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_path}aladdin_backup_{timestamp}.db"

            # Копирование файла базы данных
            import shutil

            shutil.copy2(self.db_path, backup_file)

            self.last_backup = datetime.now()
            self.log_activity(f"Создана резервная копия: {backup_file}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка создания резервной копии: {e}", "error")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Получение статистики базы данных

        Returns:
            Dict[str, Any]: Статистика базы данных
        """
        stats = {
            "total_queries": self.query_count,
            "error_count": self.error_count,
            "active_connections": self.active_connections,
            "last_backup": self.last_backup.isoformat() if self.last_backup else None,
        }

        # Получение количества записей в таблицах
        tables = [
            "users",
            "security_events",
            "threats",
            "audit_log",
            "configurations",
            "metrics",
        ]
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = self.execute_query(query)
            if result:
                stats[f"{table}_count"] = result[0]["count"]

        return stats

    def start(self) -> bool:
        """Запуск менеджера базы данных"""
        try:
            self.log_activity(f"Запуск менеджера базы данных {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер базы данных {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера базы данных {self.name}: {e}",
                "error")
            return False

    def stop(self) -> bool:
        """Остановка менеджера базы данных"""
        try:
            self.log_activity(f"Остановка менеджера базы данных {self.name}")

            # Закрытие всех соединений
            for connection in self.connection_pool:
                connection.disconnect()

            self.connection_pool.clear()
            self.active_connections = 0

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер базы данных {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера базы данных {self.name}: {e}",
                "error")
            return False
