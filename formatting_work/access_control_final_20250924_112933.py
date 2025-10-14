# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Access Control
Система контроля доступа и ролевая модель

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import hashlib
import os
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple

from core.base import ComponentStatus, SecurityBase


class UserRole(Enum):
    """Роли пользователей"""

    ADMIN = "admin"
    SECURITY_ANALYST = "security_analyst"
    SYSTEM_OPERATOR = "system_operator"
    MONITOR = "monitor"
    GUEST = "guest"
    READONLY = "readonly"


class Permission(Enum):
    """Разрешения"""

    # Чтение
    READ_DATA = "read_data"
    READ_LOGS = "read_logs"
    READ_CONFIG = "read_config"
    READ_REPORTS = "read_reports"

    # Запись
    WRITE_DATA = "write_data"
    WRITE_CONFIG = "write_config"
    WRITE_LOGS = "write_logs"

    # Удаление
    DELETE_DATA = "delete_data"
    DELETE_LOGS = "delete_logs"
    DELETE_CONFIG = "delete_config"

    # Выполнение
    EXECUTE_FUNCTIONS = "execute_functions"
    EXECUTE_SYSTEM_COMMANDS = "execute_system_commands"
    EXECUTE_SCRIPTS = "execute_scripts"

    # Управление
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"
    MANAGE_SYSTEM = "manage_system"

    # Безопасность
    VIEW_SECURITY_EVENTS = "view_security_events"
    MANAGE_SECURITY_RULES = "manage_security_rules"
    APPROVE_OPERATIONS = "approve_operations"
    BLOCK_OPERATIONS = "block_operations"


class User:
    """Пользователь системы"""

    def __init__(
        self, user_id: str, username: str, email: str, role: UserRole
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.permissions = set()
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True
        self.failed_login_attempts = 0
        self.locked_until = None
        self.session_timeout = 3600  # 1 час
        self.ip_whitelist = set()
        self.ip_blacklist = set()

    def add_permission(self, permission: Permission):
        """Добавление разрешения"""
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission):
        """Удаление разрешения"""
        self.permissions.discard(permission)

    def has_permission(self, permission: Permission) -> bool:
        """Проверка наличия разрешения"""
        return permission in self.permissions

    def is_locked(self) -> bool:
        """Проверка блокировки пользователя"""
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "created_at": self.created_at.isoformat(),
            "last_login": (
                self.last_login.isoformat() if self.last_login else None
            ),
            "is_active": self.is_active,
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": (
                self.locked_until.isoformat() if self.locked_until else None
            ),
            "session_timeout": self.session_timeout,
            "ip_whitelist": list(self.ip_whitelist),
            "ip_blacklist": list(self.ip_blacklist),
        }


class AccessControl(SecurityBase):
    """Система контроля доступа"""

    def __init__(
        self,
        name: str = "AccessControl",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация контроля доступа
        self.max_failed_attempts = (
            config.get("max_failed_attempts", 5) if config else 5
        )
        self.lockout_duration = (
            config.get("lockout_duration", 1800) if config else 1800
        )  # 30 минут
        self.session_timeout = (
            config.get("session_timeout", 3600) if config else 3600
        )  # 1 час
        self.enable_ip_whitelist = (
            config.get("enable_ip_whitelist", True) if config else True
        )
        self.enable_mfa = config.get("enable_mfa", False) if config else False

        # Хранилище пользователей и сессий
        self.users = {}
        self.active_sessions = {}
        self.user_sessions = {}
        self.role_permissions = {}

        # Статистика доступа
        self.total_login_attempts = 0
        self.successful_logins = 0
        self.failed_logins = 0
        self.locked_users = 0
        self.active_users = 0

        # Блокировки
        self.access_lock = threading.Lock()

    def initialize(self) -> bool:
        """Инициализация системы контроля доступа"""
        try:
            self.log_activity(
                f"Инициализация системы контроля доступа {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Создание ролевых разрешений
            self._create_role_permissions()

            # Создание системных пользователей
            self._create_system_users()

            # Инициализация сессий
            self._initialize_sessions()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Система контроля доступа {self.name} успешно инициализирована"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации системы контроля доступа: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _create_role_permissions(self):
        """Создание ролевых разрешений"""
        self.role_permissions = {
            UserRole.ADMIN: {
                Permission.READ_DATA,
                Permission.READ_LOGS,
                Permission.READ_CONFIG,
                Permission.READ_REPORTS,
                Permission.WRITE_DATA,
                Permission.WRITE_CONFIG,
                Permission.WRITE_LOGS,
                Permission.DELETE_DATA,
                Permission.DELETE_LOGS,
                Permission.DELETE_CONFIG,
                Permission.EXECUTE_FUNCTIONS,
                Permission.EXECUTE_SYSTEM_COMMANDS,
                Permission.EXECUTE_SCRIPTS,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.MANAGE_PERMISSIONS,
                Permission.MANAGE_SYSTEM,
                Permission.VIEW_SECURITY_EVENTS,
                Permission.MANAGE_SECURITY_RULES,
                Permission.APPROVE_OPERATIONS,
                Permission.BLOCK_OPERATIONS,
            },
            UserRole.SECURITY_ANALYST: {
                Permission.READ_DATA,
                Permission.READ_LOGS,
                Permission.READ_CONFIG,
                Permission.READ_REPORTS,
                Permission.WRITE_LOGS,
                Permission.EXECUTE_FUNCTIONS,
                Permission.VIEW_SECURITY_EVENTS,
                Permission.MANAGE_SECURITY_RULES,
                Permission.APPROVE_OPERATIONS,
                Permission.BLOCK_OPERATIONS,
            },
            UserRole.SYSTEM_OPERATOR: {
                Permission.READ_DATA,
                Permission.READ_LOGS,
                Permission.READ_CONFIG,
                Permission.READ_REPORTS,
                Permission.WRITE_DATA,
                Permission.WRITE_CONFIG,
                Permission.WRITE_LOGS,
                Permission.EXECUTE_FUNCTIONS,
                Permission.VIEW_SECURITY_EVENTS,
            },
            UserRole.MONITOR: {
                Permission.READ_DATA,
                Permission.READ_LOGS,
                Permission.READ_REPORTS,
                Permission.VIEW_SECURITY_EVENTS,
            },
            UserRole.READONLY: {Permission.READ_DATA, Permission.READ_REPORTS},
            UserRole.GUEST: {Permission.READ_REPORTS},
        }

    def _create_system_users(self):
        """Создание системных пользователей"""
        system_users = [
            {
                "user_id": "admin",
                "username": "admin",
                "email": "admin@aladdin.local",
                "role": UserRole.ADMIN,
            },
            {
                "user_id": "security_analyst",
                "username": "security_analyst",
                "email": "security@aladdin.local",
                "role": UserRole.SECURITY_ANALYST,
            },
            {
                "user_id": "monitor",
                "username": "monitor",
                "email": "monitor@aladdin.local",
                "role": UserRole.MONITOR,
            },
        ]

        for user_data in system_users:
            user = User(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"],
            )

            # Добавление разрешений роли
            role_permissions = self.role_permissions.get(user.role, set())
            user.permissions.update(role_permissions)

            self.users[user.user_id] = user

    def _initialize_sessions(self):
        """Инициализация сессий"""
        self.active_sessions = {}
        self.user_sessions = {}

    def authenticate_user(
        self, username: str, password: str, ip_address: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Аутентификация пользователя

        Args:
            username: Имя пользователя
            password: Пароль
            ip_address: IP адрес

        Returns:
            Tuple[bool, str, Optional[User]]: (успех, сообщение, пользователь)
        """
        try:
            with self.access_lock:
                self.total_login_attempts += 1

                # Поиск пользователя
                user = None
                for u in self.users.values():
                    if u.username == username:
                        user = u
                        break

                if not user:
                    self.failed_logins += 1
                    return False, "Пользователь не найден", None

                # Проверка активности пользователя
                if not user.is_active:
                    self.failed_logins += 1
                    return False, "Пользователь деактивирован", None

                # Проверка блокировки
                if user.is_locked():
                    self.failed_logins += 1
                    return (
                        False,
                        f"Пользователь заблокирован до {user.locked_until}",
                        None,
                    )

                # Проверка IP адреса
                if ip_address and self.enable_ip_whitelist:
                    if ip_address in user.ip_blacklist:
                        self.failed_logins += 1
                        return False, "IP адрес заблокирован", None

                    if (
                        user.ip_whitelist
                        and ip_address not in user.ip_whitelist
                    ):
                        self.failed_logins += 1
                        return False, "IP адрес не в белом списке", None

                # Проверка пароля (упрощенная версия)
                if not self._verify_password(user, password):
                    user.failed_login_attempts += 1
                    self.failed_logins += 1

                    # Блокировка при превышении лимита
                    if user.failed_login_attempts >= self.max_failed_attempts:
                        user.locked_until = datetime.now() + timedelta(
                            seconds=self.lockout_duration
                        )
                        self.locked_users += 1
                        self.log_activity(
                            f"Пользователь {username} заблокирован из-за превышения лимита попыток входа",
                            "warning",
                        )
                        return (
                            False,
                            "Пользователь заблокирован из-за превышения лимита попыток входа",
                            None,
                        )

                    return False, "Неверный пароль", None

                # Успешная аутентификация
                user.failed_login_attempts = 0
                user.last_login = datetime.now()
                user.locked_until = None
                self.successful_logins += 1
                self.active_users += 1

                self.log_activity(
                    f"Успешная аутентификация пользователя {username}"
                )
                return True, "Аутентификация успешна", user

        except Exception as e:
            self.log_activity(
                f"Ошибка аутентификации пользователя {username}: {e}", "error"
            )
            return False, f"Ошибка аутентификации: {e}", None

    def _verify_password(self, user: User, password: str) -> bool:
        """Проверка пароля (упрощенная версия)"""
        # В реальной системе здесь должна быть проверка хеша пароля
        # Для демонстрации используем простую проверку
        admin_password = os.getenv(
            "ADMIN_DEFAULT_PASSWORD", "CHANGE_IN_PRODUCTION"
        )
        analyst_password = os.getenv(
            "ANALYST_DEFAULT_PASSWORD", "CHANGE_IN_PRODUCTION"
        )
        monitor_password = os.getenv(
            "MONITOR_DEFAULT_PASSWORD", "CHANGE_IN_PRODUCTION"
        )

        if user.user_id == "admin" and password == admin_password:
            return True
        elif (
            user.user_id == "security_analyst" and password == analyst_password
        ):
            return True
        elif user.user_id == "monitor" and password == monitor_password:
            return True
        return False

    def create_session(
        self, user: User, ip_address: Optional[str] = None
    ) -> str:
        """
        Создание сессии пользователя

        Args:
            user: Пользователь
            ip_address: IP адрес

        Returns:
            str: ID сессии
        """
        try:
            session_id = self._generate_session_id(user.user_id)
            session_data = {
                "session_id": session_id,
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role,
                "permissions": user.permissions,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "ip_address": ip_address,
                "is_active": True,
            }

            self.active_sessions[session_id] = session_data

            if user.user_id not in self.user_sessions:
                self.user_sessions[user.user_id] = []
            self.user_sessions[user.user_id].append(session_id)

            self.log_activity(
                f"Создана сессия {session_id} для пользователя {user.username}"
            )
            return session_id

        except Exception as e:
            self.log_activity(
                f"Ошибка создания сессии для пользователя {user.username}: {e}",
                "error",
            )
            return ""

    def _generate_session_id(self, user_id: str) -> str:
        """Генерация ID сессии"""
        timestamp = int(time.time() * 1000)
        data = f"{user_id}_{timestamp}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()

    def validate_session(
        self, session_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Валидация сессии

        Args:
            session_id: ID сессии

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (валидна, данные сессии)
        """
        try:
            if session_id not in self.active_sessions:
                return False, None

            session = self.active_sessions[session_id]

            # Проверка активности сессии
            if not session["is_active"]:
                return False, None

            # Проверка таймаута сессии
            last_activity = session["last_activity"]
            if datetime.now() - last_activity > timedelta(
                seconds=self.session_timeout
            ):
                self._invalidate_session(session_id)
                return False, None

            # Обновление времени последней активности
            session["last_activity"] = datetime.now()

            return True, session

        except Exception as e:
            self.log_activity(
                f"Ошибка валидации сессии {session_id}: {e}", "error"
            )
            return False, None

    def check_permission(
        self, session_id: str, permission: Permission
    ) -> bool:
        """
        Проверка разрешения для сессии

        Args:
            session_id: ID сессии
            permission: Разрешение

        Returns:
            bool: Есть ли разрешение
        """
        try:
            valid, session = self.validate_session(session_id)
            if not valid or not session:
                return False

            user_permissions = session.get("permissions", set())
            return permission in user_permissions

        except Exception as e:
            self.log_activity(
                f"Ошибка проверки разрешения для сессии {session_id}: {e}",
                "error",
            )
            return False

    def _invalidate_session(self, session_id: str):
        """Инвалидация сессии"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            user_id = session["user_id"]

            # Удаление из активных сессий
            del self.active_sessions[session_id]

            # Удаление из пользовательских сессий
            if user_id in self.user_sessions:
                if session_id in self.user_sessions[user_id]:
                    self.user_sessions[user_id].remove(session_id)

                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]

            self.log_activity(f"Сессия {session_id} инвалидирована")

    def logout_user(self, session_id: str) -> bool:
        """
        Выход пользователя из системы

        Args:
            session_id: ID сессии

        Returns:
            bool: Успешность выхода
        """
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                username = session["username"]

                self._invalidate_session(session_id)
                self.active_users -= 1

                self.log_activity(f"Пользователь {username} вышел из системы")
                return True

            return False

        except Exception as e:
            self.log_activity(f"Ошибка выхода пользователя: {e}", "error")
            return False

    def create_user(
        self, user_id: str, username: str, email: str, role: UserRole
    ) -> bool:
        """
        Создание нового пользователя

        Args:
            user_id: ID пользователя
            username: Имя пользователя
            email: Email
            role: Роль

        Returns:
            bool: Успешность создания
        """
        try:
            if user_id in self.users:
                return False

            user = User(user_id, username, email, role)

            # Добавление разрешений роли
            role_permissions = self.role_permissions.get(role, set())
            user.permissions.update(role_permissions)

            self.users[user_id] = user

            self.log_activity(
                f"Создан пользователь {username} с ролью {role.value}"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка создания пользователя {username}: {e}", "error"
            )
            return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Получение разрешений пользователя"""
        if user_id in self.users:
            return self.users[user_id].permissions
        return set()

    def get_access_statistics(self) -> Dict[str, Any]:
        """Получение статистики доступа"""
        return {
            "total_users": len(self.users),
            "active_users": self.active_users,
            "active_sessions": len(self.active_sessions),
            "total_login_attempts": self.total_login_attempts,
            "successful_logins": self.successful_logins,
            "failed_logins": self.failed_logins,
            "locked_users": self.locked_users,
            "login_success_rate": (
                (self.successful_logins / self.total_login_attempts * 100)
                if self.total_login_attempts > 0
                else 0
            ),
        }

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы контроля доступа"""
        return {
            "name": self.name,
            "status": self.status.value,
            "max_failed_attempts": self.max_failed_attempts,
            "lockout_duration": self.lockout_duration,
            "session_timeout": self.session_timeout,
            "enable_ip_whitelist": self.enable_ip_whitelist,
            "enable_mfa": self.enable_mfa,
            "statistics": self.get_access_statistics(),
        }


# Глобальный экземпляр системы контроля доступа
ACCESS_CONTROL = AccessControl()
