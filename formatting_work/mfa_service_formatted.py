# -*- coding: utf-8 -*-
"""
ALADDIN Security System - MFA Service
Многофакторная аутентификация для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import base64
import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent, ThreatType


class MFAMethod(Enum):
    """Методы многофакторной аутентификации"""

    SMS = "sms"  # SMS код
    EMAIL = "email"  # Email код
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator)
    PUSH = "push"  # Push уведомление
    BIOMETRIC = "biometric"  # Биометрическая аутентификация
    BACKUP_CODE = "backup_code"  # Резервный код


class MFAStatus(Enum):
    """Статусы MFA"""

    PENDING = "pending"  # Ожидает подтверждения
    VERIFIED = "verified"  # Подтверждено
    EXPIRED = "expired"  # Истекло
    FAILED = "failed"  # Неудачно
    BLOCKED = "blocked"  # Заблокировано


class UserRole(Enum):
    """Роли пользователей"""

    CHILD = "child"  # Ребенок
    PARENT = "parent"  # Родитель
    ELDERLY = "elderly"  # Пожилой
    ADMIN = "admin"  # Администратор


@dataclass
class MFASession:
    """Сессия MFA"""

    session_id: str
    user_id: str
    device_id: str
    methods: List[MFAMethod]
    status: MFAStatus
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(minutes=10)
    )
    attempts: int = 0
    max_attempts: int = 3
    verified_methods: Set[MFAMethod] = field(default_factory=set)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MFACode:
    """Код MFA"""

    code_id: str
    session_id: str
    method: MFAMethod
    code: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(minutes=5)
    )
    attempts: int = 0
    max_attempts: int = 3
    is_used: bool = False


@dataclass
class UserMFAProfile:
    """Профиль MFA пользователя"""

    user_id: str
    role: UserRole
    enabled_methods: Set[MFAMethod]
    totp_secret: Optional[str] = None
    backup_codes: List[str] = field(default_factory=list)
    phone_number: Optional[str] = None
    email: Optional[str] = None
    biometric_enabled: bool = False
    last_used: Optional[datetime] = None
    failed_attempts: int = 0
    is_locked: bool = False
    lock_until: Optional[datetime] = None


class MFAService(SecurityBase):
    """
    Многофакторная аутентификация для семей
    Поддерживает различные методы аутентификации в зависимости от возраста и роли
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("MFAService", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.user_profiles: Dict[str, UserMFAProfile] = {}
        self.active_sessions: Dict[str, MFASession] = {}
        self.mfa_codes: Dict[str, MFACode] = {}
        self.blocked_users: Set[str] = set()
        self.activity_log: List[SecurityEvent] = []

        # Настройки по умолчанию
        self.session_timeout = timedelta(minutes=10)
        self.code_timeout = timedelta(minutes=5)
        self.max_failed_attempts = 3
        self.lockout_duration = timedelta(minutes=30)

        # Методы по умолчанию для разных ролей
        self.default_methods = {
            UserRole.CHILD: [MFAMethod.PUSH, MFAMethod.BIOMETRIC],
            UserRole.PARENT: [MFAMethod.SMS, MFAMethod.EMAIL, MFAMethod.TOTP],
            UserRole.ELDERLY: [MFAMethod.SMS, MFAMethod.PUSH],
            UserRole.ADMIN: [
                MFAMethod.TOTP,
                MFAMethod.BIOMETRIC,
                MFAMethod.BACKUP_CODE,
            ],
        }

        self._initialize_default_profiles()

    def _initialize_default_profiles(self) -> None:
        """Инициализация профилей по умолчанию"""
        try:
            # Создаем тестовые профили для демонстрации
            test_profiles = [
                UserMFAProfile(
                    user_id="child_1",
                    role=UserRole.CHILD,
                    enabled_methods=set(self.default_methods[UserRole.CHILD]),
                    phone_number="+1234567890",
                    email="child1@family.com",
                ),
                UserMFAProfile(
                    user_id="parent_1",
                    role=UserRole.PARENT,
                    enabled_methods=set(self.default_methods[UserRole.PARENT]),
                    phone_number="+1234567891",
                    email="parent1@family.com",
                ),
                UserMFAProfile(
                    user_id="elderly_1",
                    role=UserRole.ELDERLY,
                    enabled_methods=set(
                        self.default_methods[UserRole.ELDERLY]
                    ),
                    phone_number="+1234567892",
                    email="elderly1@family.com",
                ),
            ]

            for profile in test_profiles:
                self.user_profiles[profile.user_id] = profile

            self.logger.info("Инициализированы профили MFA по умолчанию")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации профилей: {e}")

    def create_user_profile(
        self,
        user_id: str,
        role: UserRole,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """
        Создание профиля MFA для пользователя
        Args:
            user_id: ID пользователя
            role: Роль пользователя
            phone_number: Номер телефона
            email: Email адрес
        Returns:
            bool: True если профиль создан
        """
        try:
            if user_id in self.user_profiles:
                self.logger.warning(
                    f"Профиль пользователя {user_id} уже существует"
                )
                return False

            # Создаем профиль с методами по умолчанию для роли
            profile = UserMFAProfile(
                user_id=user_id,
                role=role,
                enabled_methods=set(
                    self.default_methods.get(role, [MFAMethod.SMS])
                ),
                phone_number=phone_number,
                email=email,
            )

            # Генерируем резервные коды
            profile.backup_codes = self._generate_backup_codes()

            self.user_profiles[user_id] = profile

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="mfa_profile_created",
                severity=IncidentSeverity.LOW,
                description=f"Создан профиль MFA для пользователя {user_id} с ролью {role.value}",
                source="MFAService",
            )
            self.activity_log.append(event)

            self.logger.info(f"Создан профиль MFA для пользователя {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания профиля MFA: {e}")
            return False

    def start_mfa_session(
        self, user_id: str, device_id: str, context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Начало сессии MFA
        Args:
            user_id: ID пользователя
            device_id: ID устройства
            context: Контекст запроса
        Returns:
            Optional[str]: ID сессии или None
        """
        try:
            # Проверяем, существует ли профиль пользователя
            if user_id not in self.user_profiles:
                self.logger.warning(
                    f"Профиль пользователя {user_id} не найден"
                )
                return None

            profile = self.user_profiles[user_id]

            # Проверяем, не заблокирован ли пользователь
            if user_id in self.blocked_users:
                self.logger.warning(f"Пользователь {user_id} заблокирован")
                return None

            if (
                profile.is_locked
                and profile.lock_until
                and profile.lock_until > datetime.now()
            ):
                self.logger.warning(
                    f"Пользователь {user_id} временно заблокирован"
                )
                return None

            # Создаем сессию MFA
            session_id = f"mfa_{user_id}_{int(time.time())}"
            session = MFASession(
                session_id=session_id,
                user_id=user_id,
                device_id=device_id,
                methods=list(profile.enabled_methods),
                status=MFAStatus.PENDING,
                context=context,
            )

            self.active_sessions[session_id] = session

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="mfa_session_started",
                severity=IncidentSeverity.LOW,
                description=f"Начата сессия MFA для пользователя {user_id}",
                source="MFAService",
            )
            self.activity_log.append(event)

            self.logger.info(
                f"Начата сессия MFA {session_id} для пользователя {user_id}"
            )
            return session_id

        except Exception as e:
            self.logger.error(f"Ошибка начала сессии MFA: {e}")
            return None

    def send_mfa_code(self, session_id: str, method: MFAMethod) -> bool:
        """
        Отправка кода MFA
        Args:
            session_id: ID сессии
            method: Метод отправки
        Returns:
            bool: True если код отправлен
        """
        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"Сессия {session_id} не найдена")
                return False

            session = self.active_sessions[session_id]

            # Проверяем, не истекла ли сессия
            if session.expires_at < datetime.now():
                session.status = MFAStatus.EXPIRED
                self.logger.warning(f"Сессия {session_id} истекла")
                return False

            # Проверяем, поддерживается ли метод
            if method not in session.methods:
                self.logger.warning(
                    f"Метод {method.value} не поддерживается для сессии {session_id}"
                )
                return False

            # Генерируем код
            code = self._generate_code(method)

            # Создаем объект кода
            code_id = f"code_{session_id}_{int(time.time())}"
            mfa_code = MFACode(
                code_id=code_id,
                session_id=session_id,
                method=method,
                code=code,
            )

            self.mfa_codes[code_id] = mfa_code

            # Отправляем код (симуляция)
            success = self._deliver_code(session.user_id, method, code)

            if success:
                # Создаем событие безопасности
                event = SecurityEvent(
                    event_type="mfa_code_sent",
                    severity=IncidentSeverity.LOW,
                    description=f"Отправлен код MFA методом {method.value} для сессии {session_id}",
                    source="MFAService",
                )
                self.activity_log.append(event)

                self.logger.info(
                    f"Отправлен код MFA методом {method.value} для сессии {session_id}"
                )
                return True
            else:
                self.logger.error(
                    f"Ошибка отправки кода MFA методом {method.value}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки кода MFA: {e}")
            return False

    def verify_mfa_code(
        self, session_id: str, method: MFAMethod, code: str
    ) -> Tuple[bool, str]:
        """
        Проверка кода MFA
        Args:
            session_id: ID сессии
            method: Метод аутентификации
            code: Введенный код
        Returns:
            Tuple[bool, str]: (успешно, сообщение)
        """
        try:
            if session_id not in self.active_sessions:
                return False, "Сессия не найдена"

            session = self.active_sessions[session_id]

            # Проверяем, не истекла ли сессия
            if session.expires_at < datetime.now():
                session.status = MFAStatus.EXPIRED
                return False, "Сессия истекла"

            # Проверяем количество попыток
            if session.attempts >= session.max_attempts:
                session.status = MFAStatus.BLOCKED
                self._lock_user(session.user_id)
                return False, "Превышено количество попыток"

            # Ищем код
            valid_code = None
            for code_obj in self.mfa_codes.values():
                if (
                    code_obj.session_id == session_id
                    and code_obj.method == method
                    and not code_obj.is_used
                    and code_obj.expires_at > datetime.now()
                ):
                    valid_code = code_obj
                    break

            if not valid_code:
                session.attempts += 1
                return False, "Код не найден или истек"

            # Проверяем код
            if valid_code.attempts >= valid_code.max_attempts:
                valid_code.is_used = True
                session.attempts += 1
                return False, "Превышено количество попыток для кода"

            if self._verify_code(valid_code, code):
                # Код верный
                valid_code.is_used = True
                session.verified_methods.add(method)
                session.attempts = 0  # Сбрасываем счетчик попыток

                # Проверяем, достаточно ли методов для завершения
                required_methods = self._get_required_methods(session.user_id)
                if len(session.verified_methods) >= required_methods:
                    session.status = MFAStatus.VERIFIED

                    # Обновляем профиль пользователя
                    profile = self.user_profiles[session.user_id]
                    profile.last_used = datetime.now()
                    profile.failed_attempts = 0
                    profile.is_locked = False
                    profile.lock_until = None

                # Создаем событие безопасности
                event = SecurityEvent(
                    event_type="mfa_code_verified",
                    severity=IncidentSeverity.LOW,
                    description=f"Подтвержден код MFA методом {method.value} для сессии {session_id}",
                    source="MFAService",
                )
                self.activity_log.append(event)

                return True, "Код подтвержден"
            else:
                # Код неверный
                valid_code.attempts += 1
                session.attempts += 1

                # Проверяем, не превышено ли количество попыток
                if session.attempts >= session.max_attempts:
                    session.status = MFAStatus.BLOCKED
                    self._lock_user(session.user_id)
                    return False, "Превышено количество попыток"

                return False, "Неверный код"

        except Exception as e:
            self.logger.error(f"Ошибка проверки кода MFA: {e}")
            return False, f"Ошибка системы: {e}"

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса сессии MFA
        Args:
            session_id: ID сессии
        Returns:
            Optional[Dict[str, Any]]: Статус сессии
        """
        try:
            if session_id not in self.active_sessions:
                return None

            session = self.active_sessions[session_id]

            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "device_id": session.device_id,
                "status": session.status.value,
                "methods": [method.value for method in session.methods],
                "verified_methods": [
                    method.value for method in session.verified_methods
                ],
                "attempts": session.attempts,
                "max_attempts": session.max_attempts,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "is_expired": session.expires_at < datetime.now(),
                "required_methods": self._get_required_methods(
                    session.user_id
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса сессии: {e}")
            return None

    def cleanup_expired_sessions(self) -> int:
        """
        Очистка истекших сессий
        Returns:
            int: Количество удаленных сессий
        """
        try:
            current_time = datetime.now()
            expired_sessions = []

            for session_id, session in self.active_sessions.items():
                if session.expires_at < current_time:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.active_sessions[session_id]

            # Очищаем истекшие коды
            expired_codes = []
            for code_id, code in self.mfa_codes.items():
                if code.expires_at < current_time:
                    expired_codes.append(code_id)

            for code_id in expired_codes:
                del self.mfa_codes[code_id]

            if expired_sessions or expired_codes:
                self.logger.info(
                    f"Очищено {len(expired_sessions)} сессий и {len(expired_codes)} кодов"
                )

            return len(expired_sessions)

        except Exception as e:
            self.logger.error(f"Ошибка очистки истекших сессий: {e}")
            return 0

    def _generate_code(self, method: MFAMethod) -> str:
        """Генерация кода в зависимости от метода"""
        if method == MFAMethod.TOTP:
            # Для TOTP генерируем 6-значный код
            return f"{secrets.randbelow(1000000):06d}"
        elif method in [MFAMethod.SMS, MFAMethod.EMAIL]:
            # Для SMS и Email генерируем 6-значный код
            return f"{secrets.randbelow(1000000):06d}"
        elif method == MFAMethod.BACKUP_CODE:
            # Для резервных кодов генерируем 8-значный код
            return f"{secrets.randbelow(100000000):08d}"
        else:
            # Для других методов генерируем случайный код
            return secrets.token_hex(4)

    def _generate_backup_codes(self) -> List[str]:
        """Генерация резервных кодов"""
        codes = []
        for _ in range(10):
            code = f"{secrets.randbelow(100000000):08d}"
            codes.append(code)
        return codes

    def _deliver_code(
        self, user_id: str, method: MFAMethod, code: str
    ) -> bool:
        """Доставка кода пользователю (симуляция)"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return False

            if method == MFAMethod.SMS and profile.phone_number:
                # Симуляция отправки SMS
                self.logger.info(
                    f"SMS код {code} отправлен на {profile.phone_number}"
                )
                return True
            elif method == MFAMethod.EMAIL and profile.email:
                # Симуляция отправки Email
                self.logger.info(
                    f"Email код {code} отправлен на {profile.email}"
                )
                return True
            elif method == MFAMethod.PUSH:
                # Симуляция push уведомления
                self.logger.info(f"Push уведомление с кодом {code} отправлено")
                return True
            elif method == MFAMethod.TOTP:
                # TOTP коды генерируются локально
                self.logger.info(f"TOTP код {code} сгенерирован")
                return True
            elif method == MFAMethod.BIOMETRIC:
                # Биометрическая аутентификация
                self.logger.info(f"Запрос биометрической аутентификации")
                return True
            elif method == MFAMethod.BACKUP_CODE:
                # Резервные коды уже есть у пользователя
                self.logger.info(f"Использован резервный код")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка доставки кода: {e}")
            return False

    def _verify_code(self, mfa_code: MFACode, input_code: str) -> bool:
        """Проверка кода"""
        try:
            if mfa_code.method == MFAMethod.TOTP:
                # Для TOTP проверяем код с учетом времени
                return self._verify_totp_code(mfa_code, input_code)
            else:
                # Для остальных методов простое сравнение
                return mfa_code.code == input_code

        except Exception as e:
            self.logger.error(f"Ошибка проверки кода: {e}")
            return False

    def _verify_totp_code(self, mfa_code: MFACode, input_code: str) -> bool:
        """Проверка TOTP кода (упрощенная версия)"""
        try:
            # В реальной реализации здесь была бы проверка TOTP
            # Для демонстрации просто сравниваем коды
            return mfa_code.code == input_code

        except Exception as e:
            self.logger.error(f"Ошибка проверки TOTP кода: {e}")
            return False

    def _get_required_methods(self, user_id: str) -> int:
        """Получение количества требуемых методов для роли"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return 1

            # Количество требуемых методов в зависимости от роли
            role_requirements = {
                UserRole.CHILD: 1,  # Детям достаточно одного метода
                UserRole.PARENT: 2,  # Родителям нужно два метода
                UserRole.ELDERLY: 1,  # Пожилым достаточно одного метода
                UserRole.ADMIN: 2,  # Администраторам нужно два метода
            }

            return role_requirements.get(profile.role, 1)

        except Exception as e:
            self.logger.error(f"Ошибка получения требований методов: {e}")
            return 1

    def _lock_user(self, user_id: str) -> None:
        """Блокировка пользователя"""
        try:
            profile = self.user_profiles.get(user_id)
            if profile:
                profile.is_locked = True
                profile.lock_until = datetime.now() + self.lockout_duration
                profile.failed_attempts += 1

                # Создаем событие безопасности
                event = SecurityEvent(
                    event_type="user_locked",
                    severity=IncidentSeverity.MEDIUM,
                    description=f"Пользователь {user_id} заблокирован из-за превышения попыток MFA",
                    source="MFAService",
                )
                self.activity_log.append(event)

                self.logger.warning(
                    f"Пользователь {user_id} заблокирован до {profile.lock_until}"
                )

        except Exception as e:
            self.logger.error(f"Ошибка блокировки пользователя: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса MFA Service
        Returns:
            Dict[str, Any]: Статус сервиса
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()

            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_users": len(self.user_profiles),
                "active_sessions": len(self.active_sessions),
                "pending_sessions": len(
                    [
                        s
                        for s in self.active_sessions.values()
                        if s.status == MFAStatus.PENDING
                    ]
                ),
                "verified_sessions": len(
                    [
                        s
                        for s in self.active_sessions.values()
                        if s.status == MFAStatus.VERIFIED
                    ]
                ),
                "expired_sessions": len(
                    [
                        s
                        for s in self.active_sessions.values()
                        if s.expires_at < datetime.now()
                    ]
                ),
                "total_codes": len(self.mfa_codes),
                "blocked_users": len(self.blocked_users),
                "locked_users": len(
                    [p for p in self.user_profiles.values() if p.is_locked]
                ),
                "users_by_role": {
                    role.value: len(
                        [
                            p
                            for p in self.user_profiles.values()
                            if p.role == role
                        ]
                    )
                    for role in UserRole
                },
                "methods_usage": {
                    method.value: len(
                        [
                            s
                            for s in self.active_sessions.values()
                            if method in s.methods
                        ]
                    )
                    for method in MFAMethod
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
