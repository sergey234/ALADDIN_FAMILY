"""
AuthenticationManager - Менеджер аутентификации
Критически важный компонент системы безопасности ALADDIN
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Методы аутентификации"""

    PASSWORD = "password"
    BIOMETRIC = "biometric"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    OTP = "otp"
    FIDO2 = "fido2"
    SSO = "sso"


class AuthStatus(Enum):
    """Статусы аутентификации"""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    LOCKED = "locked"
    DISABLED = "disabled"


class SecurityLevel(Enum):
    """Уровни безопасности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserCredentials:
    """Учетные данные пользователя"""

    user_id: str
    username: str
    password_hash: str
    salt: str
    auth_methods: List[AuthMethod] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    is_locked: bool = False
    lockout_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    biometric_data: Optional[Dict[str, Any]] = None
    certificates: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


@dataclass
class AuthSession:
    """Сессия аутентификации"""

    session_id: str
    user_id: str
    auth_method: AuthMethod
    security_level: SecurityLevel
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.now)
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))


@dataclass
class AuthResult:
    """Результат аутентификации"""

    success: bool
    status: AuthStatus
    session: Optional[AuthSession] = None
    error_message: Optional[str] = None
    security_level: Optional[SecurityLevel] = None
    requires_mfa: bool = False
    mfa_challenge: Optional[str] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthPolicy:
    """Политика аутентификации"""

    min_password_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    require_mfa_for_high_security: bool = True
    allowed_auth_methods: List[AuthMethod] = field(
        default_factory=lambda: [AuthMethod.PASSWORD, AuthMethod.BIOMETRIC]
    )
    password_history_count: int = 5
    password_expiry_days: int = 90


class AuthenticationManager:
    """Менеджер аутентификации системы ALADDIN"""

    def __init__(self):
        self.users: Dict[str, UserCredentials] = {}
        self.sessions: Dict[str, AuthSession] = {}
        self.policy = AuthPolicy()
        self.password_history: Dict[str, List[str]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.risk_engine_enabled = True
        self.rate_limiter: Dict[str, List[float]] = {}

        logger.info("AuthenticationManager инициализирован")

    async def register_user(
        self,
        username: str,
        password: str,
        auth_methods: List[AuthMethod] = None,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
    ) -> bool:
        """Регистрация нового пользователя"""
        try:
            if username in self.users:
                logger.warning(f"Пользователь {username} уже существует")
                return False

            # Проверка политики пароля
            if not self._validate_password_policy(password):
                logger.warning(
                    "Пароль не соответствует политике безопасности"
                )
                return False

            # Генерация соли и хеша пароля
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)

            # Создание учетных данных
            user_id = secrets.token_urlsafe(16)
            credentials = UserCredentials(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                salt=salt,
                auth_methods=auth_methods or [AuthMethod.PASSWORD],
                security_level=security_level,
            )

            self.users[username] = credentials
            self.password_history[username] = [password_hash]

            # Логирование
            self._log_auth_event(
                "user_registered",
                username,
                {
                    "user_id": user_id,
                    "security_level": security_level.value,
                    "auth_methods": [
                        method.value for method in auth_methods or []
                    ],
                },
            )

            logger.info(f"Пользователь {username} успешно зарегистрирован")
            return True

        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя {username}: {e}")
            return False

    async def authenticate(
        self,
        username: str,
        password: str,
        auth_method: AuthMethod = AuthMethod.PASSWORD,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
    ) -> AuthResult:
        """Аутентификация пользователя"""
        try:
            # Проверка существования пользователя
            if username not in self.users:
                self._log_auth_event(
                    "auth_failed",
                    username,
                    {"reason": "user_not_found", "ip_address": ip_address},
                )
                return AuthResult(
                    success=False,
                    status=AuthStatus.FAILED,
                    error_message="Пользователь не найден",
                )

            user = self.users[username]

            # Проверка блокировки
            if (
                user.is_locked
                and user.lockout_until
                and datetime.now() < user.lockout_until
            ):
                self._log_auth_event(
                    "auth_failed",
                    username,
                    {"reason": "account_locked", "ip_address": ip_address},
                )
                return AuthResult(
                    success=False,
                    status=AuthStatus.LOCKED,
                    error_message="Аккаунт заблокирован",
                )

            # Проверка отключенного аккаунта
            if user.is_locked and not user.lockout_until:
                self._log_auth_event(
                    "auth_failed",
                    username,
                    {"reason": "account_disabled", "ip_address": ip_address},
                )
                return AuthResult(
                    success=False,
                    status=AuthStatus.DISABLED,
                    error_message="Аккаунт отключен",
                )

            # Проверка метода аутентификации
            if auth_method not in user.auth_methods:
                self._log_auth_event(
                    "auth_failed",
                    username,
                    {
                        "reason": "invalid_auth_method",
                        "ip_address": ip_address,
                    },
                )
                return AuthResult(
                    success=False,
                    status=AuthStatus.FAILED,
                    error_message="Неподдерживаемый метод аутентификации",
                )

            # Проверка пароля
            if auth_method == AuthMethod.PASSWORD:
                if not self._verify_password(
                    password, user.password_hash, user.salt
                ):
                    await self._handle_failed_attempt(username)
                    self._log_auth_event(
                        "auth_failed",
                        username,
                        {
                            "reason": "invalid_password",
                            "ip_address": ip_address,
                        },
                    )
                    return AuthResult(
                        success=False,
                        status=AuthStatus.FAILED,
                        error_message="Неверный пароль",
                    )

            # Сброс счетчика неудачных попыток
            user.failed_attempts = 0
            user.is_locked = False
            user.lockout_until = None
            user.last_login = datetime.now()

            # Создание сессии
            session = await self._create_session(
                username, auth_method, ip_address, user_agent
            )

            # Проверка необходимости MFA
            requires_mfa = user.mfa_enabled or (
                user.security_level
                in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
                and self.policy.require_mfa_for_high_security
            )

            if requires_mfa:
                mfa_challenge = await self._generate_mfa_challenge(username)
                self._log_auth_event(
                    "auth_success_mfa_required",
                    username,
                    {
                        "session_id": session.session_id,
                        "ip_address": ip_address,
                    },
                )
                return AuthResult(
                    success=True,
                    status=AuthStatus.PENDING,
                    session=session,
                    requires_mfa=True,
                    mfa_challenge=mfa_challenge,
                    security_level=user.security_level,
                )

            # Успешная аутентификация
            self._log_auth_event(
                "auth_success",
                username,
                {
                    "session_id": session.session_id,
                    "ip_address": ip_address,
                    "auth_method": auth_method.value,
                },
            )

            return AuthResult(
                success=True,
                status=AuthStatus.SUCCESS,
                session=session,
                security_level=user.security_level,
            )

        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя {username}: {e}")
            return AuthResult(
                success=False,
                status=AuthStatus.FAILED,
                error_message="Внутренняя ошибка системы",
            )

    async def verify_session(self, session_id: str) -> bool:
        """Проверка валидности сессии"""
        try:
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]

            # Проверка активности сессии
            if not session.is_active:
                return False

            # Проверка срока действия
            if datetime.now() > session.expires_at:
                session.is_active = False
                self._log_auth_event(
                    "session_expired",
                    session.user_id,
                    {"session_id": session_id},
                )
                return False

            # Обновление времени последней активности
            session.last_activity = datetime.now()

            return True

        except Exception as e:
            logger.error(f"Ошибка проверки сессии {session_id}: {e}")
            return False

    async def logout(self, session_id: str) -> bool:
        """Выход из системы"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.is_active = False

                self._log_auth_event(
                    "user_logout", session.user_id, {"session_id": session_id}
                )

                logger.info(f"Пользователь {session.user_id} вышел из системы")
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка выхода из системы {session_id}: {e}")
            return False

    async def change_password(
        self, username: str, old_password: str, new_password: str
    ) -> bool:
        """Смена пароля"""
        try:
            if username not in self.users:
                return False

            user = self.users[username]

            # Проверка старого пароля
            if not self._verify_password(
                old_password, user.password_hash, user.salt
            ):
                self._log_auth_event(
                    "password_change_failed",
                    username,
                    {"reason": "invalid_old_password"},
                )
                return False

            # Проверка политики нового пароля
            if not self._validate_password_policy(new_password):
                self._log_auth_event(
                    "password_change_failed",
                    username,
                    {"reason": "password_policy_violation"},
                )
                return False

            # Проверка истории паролей
            new_hash = self._hash_password(new_password, user.salt)
            if new_hash in self.password_history.get(username, []):
                self._log_auth_event(
                    "password_change_failed",
                    username,
                    {"reason": "password_reuse"},
                )
                return False

            # Обновление пароля
            user.password_hash = new_hash
            user.salt = secrets.token_hex(32)  # Новая соль
            user.password_hash = self._hash_password(new_password, user.salt)

            # Обновление истории паролей
            self.password_history[username].append(user.password_hash)
            if (
                len(self.password_history[username])
                > self.policy.password_history_count
            ):
                self.password_history[username].pop(0)

            self._log_auth_event("password_changed", username, {})
            logger.info(f"Пароль пользователя {username} изменен")
            return True

        except Exception as e:
            logger.error(f"Ошибка смены пароля для {username}: {e}")
            return False

    def _hash_password(self, password: str, salt: str) -> str:
        """Хеширование пароля с солью"""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        ).hex()

    def _verify_password(
        self, password: str, stored_hash: str, salt: str
    ) -> bool:
        """Проверка пароля"""
        return self._hash_password(password, salt) == stored_hash

    def _validate_password_policy(self, password: str) -> bool:
        """Проверка соответствия пароля политике безопасности"""
        if len(password) < self.policy.min_password_length:
            return False

        if self.policy.require_uppercase and not any(
            c.isupper() for c in password
        ):
            return False

        if self.policy.require_lowercase and not any(
            c.islower() for c in password
        ):
            return False

        if self.policy.require_numbers and not any(
            c.isdigit() for c in password
        ):
            return False

        if self.policy.require_special_chars and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            return False

        return True

    async def _handle_failed_attempt(self, username: str):
        """Обработка неудачной попытки входа"""
        user = self.users[username]
        user.failed_attempts += 1

        if user.failed_attempts >= self.policy.max_failed_attempts:
            user.is_locked = True
            user.lockout_until = datetime.now() + timedelta(
                minutes=self.policy.lockout_duration_minutes
            )

            self._log_auth_event(
                "account_locked",
                username,
                {
                    "failed_attempts": user.failed_attempts,
                    "lockout_until": user.lockout_until.isoformat(),
                },
            )

            logger.warning(
                f"Аккаунт {username} заблокирован из-за превышения "
                f"лимита неудачных попыток"
            )

    async def _create_session(
        self,
        username: str,
        auth_method: AuthMethod,
        ip_address: str,
        user_agent: str,
    ) -> AuthSession:
        """Создание новой сессии"""
        user = self.users[username]
        session_id = secrets.token_urlsafe(32)

        session = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            auth_method=auth_method,
            security_level=user.security_level,
            created_at=datetime.now(),
            expires_at=datetime.now()
            + timedelta(minutes=self.policy.session_timeout_minutes),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session_id] = session
        return session

    async def _generate_mfa_challenge(self, username: str) -> str:
        """Генерация MFA вызова"""
        # Простая реализация - в реальной системе здесь будет
        # интеграция с MFA провайдерами
        challenge = secrets.token_urlsafe(16)
        logger.info(f"MFA вызов для {username}: {challenge}")
        return challenge

    def _log_auth_event(
        self, event_type: str, username: str, metadata: Dict[str, Any]
    ):
        """Логирование событий аутентификации"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "username": username,
            "metadata": metadata,
        }
        self.audit_log.append(event)
        logger.info(f"Auth event: {event_type} for {username}")

    async def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе по сессии"""
        try:
            if session_id not in self.sessions:
                return None

            session = self.sessions[session_id]
            if not session.is_active:
                return None

            # Найти пользователя по user_id
            user = None
            for u in self.users.values():
                if u.user_id == session.user_id:
                    user = u
                    break

            if not user:
                return None

            return {
                "user_id": user.user_id,
                "username": user.username,
                "security_level": user.security_level.value,
                "auth_methods": [method.value for method in user.auth_methods],
                "last_login": (
                    user.last_login.isoformat() if user.last_login else None
                ),
                "permissions": user.permissions,
                "session_created": session.created_at.isoformat(),
                "session_expires": session.expires_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера аутентификации"""
        return {
            "status": "active",
            "version": "1.0.0",
            "users_count": len(self.users),
            "active_sessions": len(
                [s for s in self.sessions.values() if s.is_active]
            ),
            "total_sessions": len(self.sessions),
            "policy": {
                "min_password_length": self.policy.min_password_length,
                "max_failed_attempts": self.policy.max_failed_attempts,
                "session_timeout_minutes": self.policy.session_timeout_minutes,
                "require_mfa_for_high_security": (
                    self.policy.require_mfa_for_high_security
                ),
            },
            "audit_events_count": len(self.audit_log),
            "risk_engine_enabled": self.risk_engine_enabled,
        }

    def __str__(self) -> str:
        """Строковое представление объекта"""
        return (f"AuthenticationManager(users={len(self.users)}, "
                f"sessions={len(self.sessions)})")

    def __repr__(self) -> str:
        """Представление для отладки"""
        return (f"AuthenticationManager(users={len(self.users)}, "
                f"sessions={len(self.sessions)}, policy={self.policy})")

    def __eq__(self, other) -> bool:
        """Сравнение объектов"""
        if not isinstance(other, AuthenticationManager):
            return False
        return (len(self.users) == len(other.users) and
                len(self.sessions) == len(other.sessions))

    def __len__(self) -> int:
        """Количество активных сессий"""
        return len(self.sessions)

    def __iter__(self):
        """Итерация по активным сессиям"""
        return iter(self.sessions.values())

    def __contains__(self, session_id: str) -> bool:
        """Проверка наличия сессии"""
        return session_id in self.sessions

    def __enter__(self):
        """Контекстный менеджер - вход"""
        logger.info("AuthenticationManager: вход в контекст")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        logger.info("AuthenticationManager: выход из контекста")
        if exc_type:
            logger.error(f"Ошибка в контексте: {exc_val}")

    @property
    def is_active(self) -> bool:
        """Проверка активности менеджера"""
        return len(self.sessions) > 0

    @property
    def users_count(self) -> int:
        """Количество зарегистрированных пользователей"""
        return len(self.users)

    @property
    def sessions_count(self) -> int:
        """Количество активных сессий"""
        return len(self.sessions)

    @property
    def status_info(self) -> Dict[str, Any]:
        """Информация о статусе"""
        return {
            "users_count": len(self.users),
            "sessions_count": len(self.sessions),
            "is_active": self.is_active,
            "risk_engine_enabled": self.risk_engine_enabled
        }

    @staticmethod
    def get_supported_auth_methods() -> List[AuthMethod]:
        """Получить поддерживаемые методы аутентификации"""
        return list(AuthMethod)

    @staticmethod
    def get_supported_security_levels() -> List[SecurityLevel]:
        """Получить поддерживаемые уровни безопасности"""
        return list(SecurityLevel)

    @classmethod
    def create_with_custom_policy(
        cls, policy: AuthPolicy
    ) -> 'AuthenticationManager':
        """Создать экземпляр с пользовательской политикой"""
        instance = cls()
        instance.policy = policy
        return instance


# Создание глобального экземпляра
authentication_manager = AuthenticationManager()
