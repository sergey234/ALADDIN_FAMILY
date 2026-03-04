#!/usr/bin/env python3
"""
AccessControlManager - P0 критический компонент
Управление доступом и ролевой моделью безопасности
"""

import hashlib
import logging
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from security.core.security_base import ComponentStatus, SecurityBase


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

    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    EXECUTE_FUNCTIONS = "execute_functions"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SECURITY_EVENTS = "view_security_events"
    MANAGE_SECURITY_RULES = "manage_security_rules"


class AccessLevel(Enum):
    """Уровни доступа"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AccessControlManager(SecurityBase):
    """Менеджер контроля доступа - P0 критический компонент"""

    def __init__(
        self,
        name: str = "AccessControlManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Пользователи и роли
        self.users: Dict[str, Dict[str, Any]] = {}
        self.roles: Dict[UserRole, Set[Permission]] = {}
        self.user_roles: Dict[str, Set[UserRole]] = {}

        # Сессии и доступ
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.access_logs: List[Dict[str, Any]] = []

        # Безопасность
        self.max_failed_attempts = (
            config.get("max_failed_attempts", 5) if config else 5
        )
        self.lockout_duration = (
            config.get("lockout_duration", 1800) if config else 1800
        )
        self.session_timeout = (
            config.get("session_timeout", 3600) if config else 3600
        )

        # Статистика
        self.total_requests = 0
        self.allowed_requests = 0
        self.denied_requests = 0
        self.active_users = 0

        # Блокировки
        self.access_lock = threading.Lock()

    def initialize(self) -> bool:
        """Инициализация менеджера контроля доступа"""
        try:
            self.log_activity(
                f"Инициализация AccessControlManager {self.name}"
            )
            self.status = ComponentStatus.INITIALIZING

            # Создание ролевых разрешений
            self._create_role_permissions()

            # Создание системных пользователей
            self._create_system_users()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"AccessControlManager {self.name} успешно инициализирован"
            )
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка инициализации AccessControlManager: {e}", "error"
            )
            self.status = ComponentStatus.ERROR
            return False

    def _create_role_permissions(self):
        """Создание ролевых разрешений"""
        self.roles = {
            UserRole.ADMIN: {
                Permission.READ_DATA,
                Permission.WRITE_DATA,
                Permission.DELETE_DATA,
                Permission.EXECUTE_FUNCTIONS,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_SECURITY_EVENTS,
                Permission.MANAGE_SECURITY_RULES,
            },
            UserRole.SECURITY_ANALYST: {
                Permission.READ_DATA,
                Permission.VIEW_SECURITY_EVENTS,
                Permission.MANAGE_SECURITY_RULES,
            },
            UserRole.SYSTEM_OPERATOR: {
                Permission.READ_DATA,
                Permission.WRITE_DATA,
                Permission.EXECUTE_FUNCTIONS,
            },
            UserRole.MONITOR: {
                Permission.READ_DATA,
                Permission.VIEW_SECURITY_EVENTS,
            },
            UserRole.READONLY: {Permission.READ_DATA},
            UserRole.GUEST: set(),
        }

    def _create_system_users(self):
        """Создание системных пользователей"""
        # Администратор
        admin_user = {
            "user_id": "admin",
            "username": "admin",
            "password_hash": self._hash_password("admin123"),
            "roles": {UserRole.ADMIN},
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None,
            "failed_attempts": 0,
            "locked_until": None,
        }
        self.users["admin"] = admin_user
        self.user_roles["admin"] = {UserRole.ADMIN}

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Аутентификация пользователя"""
        try:
            with self.access_lock:
                if username not in self.users:
                    self.log_activity(
                        f"Попытка входа несуществующего пользователя: {username}",
                        "warning",
                    )
                    return None

                user = self.users[username]

                # Проверка блокировки
                if (
                    user.get("locked_until")
                    and datetime.now() < user["locked_until"]
                ):
                    self.log_activity(
                        f"Пользователь {username} заблокирован", "warning"
                    )
                    return None

                # Проверка пароля
                if user["password_hash"] != self._hash_password(password):
                    user["failed_attempts"] += 1
                    self.denied_requests += 1

                    if user["failed_attempts"] >= self.max_failed_attempts:
                        user["locked_until"] = datetime.now() + timedelta(
                            seconds=self.lockout_duration
                        )
                        self.log_activity(
                            f"Пользователь {username} заблокирован из-за неудачных попыток",
                            "warning",
                        )

                    return None

                # Успешная аутентификация
                user["failed_attempts"] = 0
                user["last_login"] = datetime.now()
                user["locked_until"] = None

                # Создание сессии
                session_id = f"session_{int(time.time())}_{username}"
                self.active_sessions[session_id] = {
                    "user_id": username,
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "ip_address": "127.0.0.1",  # В реальной системе получать из запроса
                }

                self.allowed_requests += 1
                self.total_requests += 1
                self.active_users = len(self.active_sessions)

                self.log_activity(
                    f"Успешная аутентификация пользователя: {username}"
                )
                return session_id

        except Exception as e:
            self.log_activity(f"Ошибка аутентификации: {e}", "error")
            return None

    def check_permission(
        self, session_id: str, permission: Permission
    ) -> bool:
        """Проверка разрешения для сессии"""
        try:
            with self.access_lock:
                if session_id not in self.active_sessions:
                    return False

                session = self.active_sessions[session_id]
                user_id = session["user_id"]

                # Проверка таймаута сессии
                if datetime.now() - session["last_activity"] > timedelta(
                    seconds=self.session_timeout
                ):
                    del self.active_sessions[session_id]
                    self.active_users = len(self.active_sessions)
                    return False

                # Обновление активности
                session["last_activity"] = datetime.now()

                # Проверка разрешений
                if user_id not in self.user_roles:
                    return False

                user_roles = self.user_roles[user_id]
                for role in user_roles:
                    if permission in self.roles.get(role, set()):
                        return True

                return False

        except Exception as e:
            self.log_activity(f"Ошибка проверки разрешения: {e}", "error")
            return False

    def get_user_permissions(self, session_id: str) -> Set[Permission]:
        """Получение разрешений пользователя"""
        try:
            with self.access_lock:
                if session_id not in self.active_sessions:
                    return set()

                user_id = self.active_sessions[session_id]["user_id"]
                if user_id not in self.user_roles:
                    return set()

                permissions = set()
                for role in self.user_roles[user_id]:
                    permissions.update(self.roles.get(role, set()))

                return permissions

        except Exception as e:
            self.log_activity(f"Ошибка получения разрешений: {e}", "error")
            return set()

    def logout_user(self, session_id: str) -> bool:
        """Выход пользователя из системы"""
        try:
            with self.access_lock:
                if session_id in self.active_sessions:
                    user_id = self.active_sessions[session_id]["user_id"]
                    del self.active_sessions[session_id]
                    self.active_users = len(self.active_sessions)
                    self.log_activity(
                        f"Пользователь {user_id} вышел из системы"
                    )
                    return True
                return False

        except Exception as e:
            self.log_activity(f"Ошибка выхода из системы: {e}", "error")
            return False

    def get_access_statistics(self) -> Dict[str, Any]:
        """Получение статистики доступа"""
        return {
            "total_requests": self.total_requests,
            "allowed_requests": self.allowed_requests,
            "denied_requests": self.denied_requests,
            "active_users": self.active_users,
            "total_users": len(self.users),
            "success_rate": (
                self.allowed_requests / max(self.total_requests, 1)
            )
            * 100,
        }

    def shutdown(self) -> bool:
        """Остановка менеджера контроля доступа"""
        try:
            self.log_activity("Остановка AccessControlManager...")
            self.status = ComponentStatus.STOPPED
            self.log_activity("AccessControlManager остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки AccessControlManager: {e}", "error"
            )
            return False

    # Тестирование

    def add_user(self, username: str, password: str, role: UserRole) -> bool:
        """Добавление нового пользователя"""
        try:
            if username in self.users:
                self.log_activity(
                    f"Пользователь {username} уже существует", "warning"
                )
                return False

            hashed_password = self._hash_password(password)
            self.users[username] = {
                "password": hashed_password,
                "role": role,
                "created_at": datetime.now(),
                "last_login": None,
                "failed_attempts": 0,
            }

            self.log_activity(f"Пользователь {username} добавлен", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка добавления пользователя: {e}", "error")
            return False

    def remove_user(self, username: str) -> bool:
        """Удаление пользователя"""
        try:
            if username not in self.users:
                self.log_activity(
                    f"Пользователь {username} не найден", "warning"
                )
                return False

            del self.users[username]
            self.log_activity(f"Пользователь {username} удален", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка удаления пользователя: {e}", "error")
            return False

    def create_session(self, username: str) -> Optional[str]:
        """Создание сессии пользователя"""
        try:
            if username not in self.users:
                self.log_activity(
                    f"Попытка создания сессии для несуществующего пользователя: {username}",
                    "warning",
                )
                return None

            session_id = hashlib.sha256(
                f"{username}{datetime.now()}".encode()
            ).hexdigest()[:16]
            self.active_sessions[session_id] = {
                "user_id": username,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "ip_address": "127.0.0.1",  # В реальной системе получать из запроса
            }

            self.log_activity(
                f"Создана сессия {session_id} для пользователя {username}",
                "info",
            )
            return session_id
        except Exception as e:
            self.log_activity(f"Ошибка создания сессии: {e}", "error")
            return None

    def destroy_session(self, session_id: str) -> bool:
        """Уничтожение сессии пользователя"""
        try:
            if session_id not in self.active_sessions:
                self.log_activity(f"Сессия {session_id} не найдена", "warning")
                return False

            del self.active_sessions[session_id]
            self.log_activity(f"Сессия {session_id} уничтожена", "info")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка уничтожения сессии: {e}", "error")
            return False

    def grant_permission(self, username: str, permission: Permission) -> bool:
        """Предоставление разрешения пользователю"""
        try:
            if username not in self.users:
                self.log_activity(
                    f"Пользователь {username} не найден", "warning"
                )
                return False

            if username not in self.user_roles:
                self.user_roles[username] = set()

            self.user_roles[username].add(permission)
            self.log_activity(
                f"Разрешение {permission.value} предоставлено пользователю {username}",
                "info",
            )
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка предоставления разрешения: {e}", "error"
            )
            return False

    def revoke_permission(self, username: str, permission: Permission) -> bool:
        """Отзыв разрешения у пользователя"""
        try:
            if username not in self.users:
                self.log_activity(
                    f"Пользователь {username} не найден", "warning"
                )
                return False

            if (
                username in self.user_roles
                and permission in self.user_roles[username]
            ):
                self.user_roles[username].remove(permission)
                self.log_activity(
                    f"Разрешение {permission.value} отозвано у пользователя {username}",
                    "info",
                )
                return True
            else:
                self.log_activity(
                    f"У пользователя {username} нет разрешения {permission.value}",
                    "warning",
                )
                return False
        except Exception as e:
            self.log_activity(f"Ошибка отзыва разрешения: {e}", "error")
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        try:
            if username not in self.users:
                return None

            user_info = self.users[username].copy()
            user_info["permissions"] = list(
                self.user_roles.get(username, set())
            )
            return user_info
        except Exception as e:
            self.log_activity(
                f"Ошибка получения информации о пользователе: {e}", "error"
            )
            return None

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Получение списка активных сессий"""
        try:
            return self.active_sessions.copy()
        except Exception as e:
            self.log_activity(
                f"Ошибка получения активных сессий: {e}", "error"
            )
            return {}

    def cleanup_expired_sessions(self) -> int:
        """Очистка истекших сессий"""
        try:
            current_time = datetime.now()
            expired_sessions = []

            for session_id, session_data in self.active_sessions.items():
                if current_time - session_data["last_activity"] > timedelta(
                    seconds=self.session_timeout
                ):
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.active_sessions[session_id]

            if expired_sessions:
                self.log_activity(
                    f"Очищено {len(expired_sessions)} истекших сессий", "info"
                )

            return len(expired_sessions)
        except Exception as e:
            self.log_activity(f"Ошибка очистки сессий: {e}", "error")
            return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    manager = AccessControlManager()
    if manager.initialize():
        print("✅ AccessControlManager инициализирован")

        # Тест аутентификации
        session_id = manager.authenticate_user("admin", "admin123")
        if session_id:
            print(f"✅ Аутентификация успешна: {session_id}")

            # Тест разрешений
            can_read = manager.check_permission(
                session_id, Permission.READ_DATA
            )
            can_write = manager.check_permission(
                session_id, Permission.WRITE_DATA
            )
            print(f"📊 Разрешения - Чтение: {can_read}, Запись: {can_write}")

            # Статистика
            stats = manager.get_access_statistics()
            print(f"📈 Статистика: {stats}")

        manager.shutdown()
    else:
        print("❌ Ошибка инициализации AccessControlManager")
