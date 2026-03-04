# -*- coding: utf-8 -*-
"""
ALADDIN Security System - MFAService
Многофакторная аутентификация - КРИТИЧНО #2

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import base64
import io
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import pyotp
import qrcode


class MFAStatus(Enum):
    """Статусы MFA"""

    ENABLED = "enabled"
    DISABLED = "disabled"
    PENDING = "pending"
    LOCKED = "locked"


class MFAType(Enum):
    """Типы MFA"""

    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"  # SMS код
    EMAIL = "email"  # Email код
    PUSH = "push"  # Push уведомление
    HARDWARE = "hardware"  # Аппаратный токен


@dataclass
class MFASecret:
    """Секрет MFA"""

    secret_key: str
    backup_codes: List[str]
    qr_code: str
    created_at: float
    expires_at: Optional[float] = None


@dataclass
class MFAChallenge:
    """Вызов MFA"""

    challenge_id: str
    user_id: str
    mfa_type: MFAType
    code: str
    created_at: float
    expires_at: float
    attempts: int = 0
    max_attempts: int = 3


@dataclass
class MFAConfig:
    """Конфигурация MFA"""

    totp_window: int = 1
    sms_provider: str = "default"
    email_provider: str = "default"
    backup_codes_count: int = 10
    code_length: int = 6
    code_expiry: int = 300  # 5 минут
    max_attempts: int = 3
    lockout_duration: int = 900  # 15 минут


class MFAService:
    """Сервис многофакторной аутентификации - КРИТИЧНО #2"""

    def __init__(self, config: Optional[MFAConfig] = None):
        """
        Инициализация MFAService

        Args:
            config: Конфигурация MFA
        """
        self.config = config or MFAConfig()
        self.secrets: Dict[str, MFASecret] = {}
        self.challenges: Dict[str, MFAChallenge] = {}
        self.user_mfa_status: Dict[str, MFAStatus] = {}
        self.failed_attempts: Dict[str, List[float]] = {}

        # Дополнительные атрибуты для улучшенной функциональности
        self.created_at: float = time.time()
        self.last_cleanup: float = time.time()
        self.total_attempts: int = 0
        self.successful_attempts: int = 0
        self.failed_attempts_count: int = 0

        # Инициализация провайдеров
        self.totp = pyotp.TOTP
        self.sms_provider = self._init_sms_provider()
        self.email_provider = self._init_email_provider()

    def _init_sms_provider(self) -> Any:
        """Инициализация SMS провайдера"""
        # Заглушка для SMS провайдера
        return None

    def _init_email_provider(self) -> Any:
        """Инициализация Email провайдера"""
        # Заглушка для Email провайдера
        return None

    def enable_mfa(self, user_id: str, mfa_type: MFAType) -> Dict[str, Any]:
        """
        Включение MFA для пользователя

        Args:
            user_id: ID пользователя
            mfa_type: Тип MFA

        Returns:
            Результат включения MFA
        """
        try:
            if mfa_type == MFAType.TOTP:
                return self._enable_totp(user_id)
            elif mfa_type == MFAType.SMS:
                return self._enable_sms(user_id)
            elif mfa_type == MFAType.EMAIL:
                return self._enable_email(user_id)
            else:
                return {
                    "success": False,
                    "error": f"Неподдерживаемый тип MFA: {mfa_type}",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка включения MFA: {str(e)}",
            }

    def _enable_totp(self, user_id: str) -> Dict[str, Any]:
        """Включение TOTP MFA"""
        # Генерация секретного ключа
        secret_key = pyotp.random_base32()

        # Создание TOTP объекта (для будущего использования)
        # totp = self.totp(secret_key)

        # Генерация QR кода
        qr_code = self._generate_qr_code(user_id, secret_key)

        # Генерация резервных кодов
        backup_codes = self._generate_backup_codes()

        # Сохранение секрета
        mfa_secret = MFASecret(
            secret_key=secret_key,
            backup_codes=backup_codes,
            qr_code=qr_code,
            created_at=time.time(),
        )
        self.secrets[user_id] = mfa_secret

        # Установка статуса
        self.user_mfa_status[user_id] = MFAStatus.ENABLED

        return {
            "success": True,
            "secret_key": secret_key,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "TOTP MFA успешно включен",
        }

    def _enable_sms(self, user_id: str) -> Dict[str, Any]:
        """Включение SMS MFA"""
        # Проверка наличия номера телефона
        phone_number = self._get_user_phone(user_id)
        if not phone_number:
            return {"success": False, "error": "Номер телефона не найден"}

        # Установка статуса
        self.user_mfa_status[user_id] = MFAStatus.ENABLED

        return {
            "success": True,
            "phone_number": phone_number,
            "message": "SMS MFA успешно включен",
        }

    def _enable_email(self, user_id: str) -> Dict[str, Any]:
        """Включение Email MFA"""
        # Проверка наличия email
        email = self._get_user_email(user_id)
        if not email:
            return {"success": False, "error": "Email не найден"}

        # Установка статуса
        self.user_mfa_status[user_id] = MFAStatus.ENABLED

        return {
            "success": True,
            "email": email,
            "message": "Email MFA успешно включен",
        }

    def verify_mfa(
        self, user_id: str, code: str, mfa_type: MFAType
    ) -> Dict[str, Any]:
        """
        Проверка MFA кода

        Args:
            user_id: ID пользователя
            code: MFA код
            mfa_type: Тип MFA

        Returns:
            Результат проверки
        """
        try:
            # Проверка блокировки
            if self._is_user_locked(user_id):
                return {
                    "success": False,
                    "error": (
                        "Пользователь заблокирован из-за превышения попыток"
                    ),
                }

            # Проверка статуса MFA
            if self.user_mfa_status.get(user_id) != MFAStatus.ENABLED:
                return {
                    "success": False,
                    "error": "MFA не включен для пользователя",
                }

            # Проверка кода в зависимости от типа
            if mfa_type == MFAType.TOTP:
                return self._verify_totp(user_id, code)
            elif mfa_type == MFAType.SMS:
                return self._verify_sms(user_id, code)
            elif mfa_type == MFAType.EMAIL:
                return self._verify_email(user_id, code)
            elif mfa_type == MFAType.PUSH:
                return self._verify_push(user_id, code)
            else:
                return {
                    "success": False,
                    "error": f"Неподдерживаемый тип MFA: {mfa_type}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка проверки MFA: {str(e)}",
            }

    def _verify_totp(self, user_id: str, code: str) -> Dict[str, Any]:
        """Проверка TOTP кода"""
        if user_id not in self.secrets:
            return {"success": False, "error": "MFA секрет не найден"}

        secret = self.secrets[user_id]
        totp = self.totp(secret.secret_key)

        # Проверка TOTP кода
        if totp.verify(code, valid_window=self.config.totp_window):
            self._clear_failed_attempts(user_id)
            return {"success": True, "message": "TOTP код подтвержден"}

        # Проверка резервных кодов
        if code in secret.backup_codes:
            secret.backup_codes.remove(code)
            self._clear_failed_attempts(user_id)
            return {
                "success": True,
                "message": "Резервный код подтвержден",
                "backup_code_used": True,
            }

        # Неверный код
        self._record_failed_attempt(user_id)
        return {"success": False, "error": "Неверный TOTP код"}

    def _verify_sms(self, user_id: str, code: str) -> Dict[str, Any]:
        """Проверка SMS кода"""
        # Поиск активного вызова
        challenge = self._find_active_challenge(user_id, MFAType.SMS)
        if not challenge:
            return {"success": False, "error": "SMS вызов не найден или истек"}

        # Проверка кода
        if challenge.code == code:
            self._clear_failed_attempts(user_id)
            self._remove_challenge(challenge.challenge_id)
            return {"success": True, "message": "SMS код подтвержден"}

        # Неверный код
        self._record_failed_attempt(user_id)
        return {"success": False, "error": "Неверный SMS код"}

    def _verify_email(self, user_id: str, code: str) -> Dict[str, Any]:
        """Проверка Email кода"""
        # Поиск активного вызова
        challenge = self._find_active_challenge(user_id, MFAType.EMAIL)
        if not challenge:
            return {
                "success": False,
                "error": "Email вызов не найден или истек",
            }

        # Проверка кода
        if challenge.code == code:
            self._clear_failed_attempts(user_id)
            self._remove_challenge(challenge.challenge_id)
            return {"success": True, "message": "Email код подтвержден"}

        # Неверный код
        self._record_failed_attempt(user_id)
        return {"success": False, "error": "Неверный Email код"}

    def _verify_push(self, user_id: str, code: str) -> Dict[str, Any]:
        """Проверка Push уведомления"""
        # Заглушка для Push уведомлений
        return {"success": False, "error": "Push уведомления не реализованы"}

    def send_mfa_challenge(
        self, user_id: str, mfa_type: MFAType
    ) -> Dict[str, Any]:
        """
        Отправка MFA вызова

        Args:
            user_id: ID пользователя
            mfa_type: Тип MFA

        Returns:
            Результат отправки
        """
        try:
            if mfa_type == MFAType.SMS:
                return self._send_sms_challenge(user_id)
            elif mfa_type == MFAType.EMAIL:
                return self._send_email_challenge(user_id)
            else:
                return {
                    "success": False,
                    "error": (
                        f"Отправка вызова не поддерживается для {mfa_type}"
                    ),
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка отправки вызова: {str(e)}",
            }

    def _send_sms_challenge(self, user_id: str) -> Dict[str, Any]:
        """Отправка SMS вызова"""
        phone_number = self._get_user_phone(user_id)
        if not phone_number:
            return {"success": False, "error": "Номер телефона не найден"}

        # Генерация кода
        code = self._generate_code()

        # Создание вызова
        challenge = MFAChallenge(
            challenge_id=self._generate_challenge_id(),
            user_id=user_id,
            mfa_type=MFAType.SMS,
            code=code,
            created_at=time.time(),
            expires_at=time.time() + self.config.code_expiry,
        )
        self.challenges[challenge.challenge_id] = challenge

        # Отправка SMS (заглушка)
        # self._send_sms(phone_number, code)

        return {
            "success": True,
            "challenge_id": challenge.challenge_id,
            "message": f"SMS код отправлен на {phone_number}",
        }

    def _send_email_challenge(self, user_id: str) -> Dict[str, Any]:
        """Отправка Email вызова"""
        email = self._get_user_email(user_id)
        if not email:
            return {"success": False, "error": "Email не найден"}

        # Генерация кода
        code = self._generate_code()

        # Создание вызова
        challenge = MFAChallenge(
            challenge_id=self._generate_challenge_id(),
            user_id=user_id,
            mfa_type=MFAType.EMAIL,
            code=code,
            created_at=time.time(),
            expires_at=time.time() + self.config.code_expiry,
        )
        self.challenges[challenge.challenge_id] = challenge

        # Отправка Email (заглушка)
        # self._send_email(email, code)

        return {
            "success": True,
            "challenge_id": challenge.challenge_id,
            "message": f"Email код отправлен на {email}",
        }

    def disable_mfa(self, user_id: str) -> Dict[str, Any]:
        """
        Отключение MFA для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Результат отключения
        """
        try:
            # Удаление секретов
            if user_id in self.secrets:
                del self.secrets[user_id]

            # Удаление статуса
            if user_id in self.user_mfa_status:
                del self.user_mfa_status[user_id]

            # Очистка попыток
            self._clear_failed_attempts(user_id)

            return {"success": True, "message": "MFA успешно отключен"}
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка отключения MFA: {str(e)}",
            }

    def get_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """
        Получение статуса MFA пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Статус MFA
        """
        status = self.user_mfa_status.get(user_id, MFAStatus.DISABLED)
        has_secret = user_id in self.secrets

        return {
            "user_id": user_id,
            "status": status.value,
            "has_secret": has_secret,
            "is_locked": self._is_user_locked(user_id),
            "failed_attempts": len(self.failed_attempts.get(user_id, [])),
        }

    def _generate_qr_code(self, user_id: str, secret_key: str) -> str:
        """Генерация QR кода для TOTP"""
        # Создание URI для TOTP
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user_id, issuer_name="ALADDIN Security"
        )

        # Генерация QR кода
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        # Создание изображения
        img = qr.make_image(fill_color="black", back_color="white")

        # Конвертация в base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def _generate_backup_codes(self) -> List[str]:
        """Генерация резервных кодов"""
        codes = []
        for _ in range(self.config.backup_codes_count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes

    def _generate_code(self) -> str:
        """Генерация MFA кода"""
        return secrets.randbelow(10**self.config.code_length)

    def _generate_challenge_id(self) -> str:
        """Генерация ID вызова"""
        return secrets.token_urlsafe(32)

    def _get_user_phone(self, user_id: str) -> Optional[str]:
        """Получение номера телефона пользователя"""
        # Заглушка - в реальной системе получать из базы данных
        return f"+7{secrets.randbelow(10000000000):010d}"

    def _get_user_email(self, user_id: str) -> Optional[str]:
        """Получение email пользователя"""
        # Заглушка - в реальной системе получать из базы данных
        return f"user{user_id}@example.com"

    def _find_active_challenge(
        self, user_id: str, mfa_type: MFAType
    ) -> Optional[MFAChallenge]:
        """Поиск активного вызова"""
        current_time = time.time()
        for challenge in self.challenges.values():
            if (
                challenge.user_id == user_id
                and challenge.mfa_type == mfa_type
                and challenge.expires_at > current_time
            ):
                return challenge
        return None

    def _remove_challenge(self, challenge_id: str):
        """Удаление вызова"""
        if challenge_id in self.challenges:
            del self.challenges[challenge_id]

    def _record_failed_attempt(self, user_id: str):
        """Запись неудачной попытки"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []

        current_time = time.time()
        self.failed_attempts[user_id].append(current_time)

        # Очистка старых попыток
        cutoff_time = current_time - self.config.lockout_duration
        self.failed_attempts[user_id] = [
            attempt
            for attempt in self.failed_attempts[user_id]
            if attempt > cutoff_time
        ]

    def _clear_failed_attempts(self, user_id: str):
        """Очистка неудачных попыток"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]

    def _is_user_locked(self, user_id: str) -> bool:
        """Проверка блокировки пользователя"""
        if user_id not in self.failed_attempts:
            return False

        attempts = self.failed_attempts[user_id]
        if len(attempts) >= self.config.max_attempts:
            return True

        return False

    def cleanup_expired_challenges(self):
        """Очистка истекших вызовов"""
        current_time = time.time()
        expired_challenges = [
            challenge_id
            for challenge_id, challenge in self.challenges.items()
            if challenge.expires_at <= current_time
        ]

        for challenge_id in expired_challenges:
            del self.challenges[challenge_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики MFA"""
        total_users = len(self.user_mfa_status)
        enabled_users = sum(
            1
            for status in self.user_mfa_status.values()
            if status == MFAStatus.ENABLED
        )
        locked_users = sum(
            1
            for user_id in self.user_mfa_status.keys()
            if self._is_user_locked(user_id)
        )
        active_challenges = len(self.challenges)

        return {
            "total_users": total_users,
            "enabled_users": enabled_users,
            "locked_users": locked_users,
            "active_challenges": active_challenges,
            "mfa_enabled_percentage": (
                (enabled_users / total_users * 100) if total_users > 0 else 0
            ),
        }


# Пример использования
if __name__ == "__main__":
    # Создание сервиса MFA
    mfa_service = MFAService()

    # Тестирование TOTP
    user_id = "test_user"
    result = mfa_service.enable_mfa(user_id, MFAType.TOTP)
    print(f"Включение TOTP: {result}")

    if result["success"]:
        # Получение TOTP кода
        secret = mfa_service.secrets[user_id]
        totp = pyotp.TOTP(secret.secret_key)
        current_code = totp.now()

        # Проверка кода
        verify_result = mfa_service.verify_mfa(
            user_id, current_code, MFAType.TOTP
        )
        print(f"Проверка TOTP: {verify_result}")

    # Статистика
    stats = mfa_service.get_statistics()
    print(f"Статистика MFA: {stats}")

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"MFAService(config={self.config.totp_window}min, "
            f"users={len(self.user_mfa_status)}, "
            f"challenges={len(self.challenges)})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"MFAService(config={repr(self.config)}, "
            f"secrets_count={len(self.secrets)}, "
            f"challenges_count={len(self.challenges)}, "
            f"users_count={len(self.user_mfa_status)})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, MFAService):
            return False
        return (
            self.config == other.config
            and len(self.secrets) == len(other.secrets)
            and len(self.challenges) == len(other.challenges)
        )

    def __len__(self) -> int:
        """Количество активных пользователей MFA"""
        return len(self.user_mfa_status)

    def __iter__(self):
        """Итерация по пользователям MFA"""
        return iter(self.user_mfa_status.keys())

    def __contains__(self, user_id: str) -> bool:
        """Проверка наличия пользователя в MFA"""
        return user_id in self.user_mfa_status

    def __enter__(self):
        """Контекстный менеджер - вход"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        if exc_type is not None:
            print(f"Ошибка в MFA контексте: {exc_type.__name__}: {exc_val}")
        return False  # Не подавляем исключения

    @property
    def is_active(self) -> bool:
        """Проверка активности MFA сервиса"""
        return len(self.user_mfa_status) > 0

    @property
    def users_count(self) -> int:
        """Количество пользователей MFA"""
        return len(self.user_mfa_status)

    @property
    def challenges_count(self) -> int:
        """Количество активных вызовов"""
        return len(self.challenges)

    @property
    def status_info(self) -> Dict[str, Any]:
        """Получение информации о статусе MFA"""
        return {
            "users_count": len(self.user_mfa_status),
            "challenges_count": len(self.challenges),
            "secrets_count": len(self.secrets),
            "failed_attempts": len(self.failed_attempts),
            "is_active": self.is_active,
            "total_attempts": getattr(self, 'total_attempts', 0),
            "successful_attempts": getattr(self, 'successful_attempts', 0),
            "failed_attempts_count": getattr(self, 'failed_attempts_count', 0),
            "created_at": getattr(self, 'created_at', 0),
            "last_cleanup": getattr(self, 'last_cleanup', 0),
        }

    @staticmethod
    def get_supported_types() -> List[str]:
        """Получение поддерживаемых типов MFA"""
        return [mfa_type.value for mfa_type in MFAType]

    @staticmethod
    def get_supported_statuses() -> List[str]:
        """Получение поддерживаемых статусов MFA"""
        return [status.value for status in MFAStatus]

    @classmethod
    def create_with_custom_config(
        cls, config: MFAConfig
    ) -> "MFAService":
        """Создание MFA сервиса с пользовательской конфигурацией"""
        if not isinstance(config, MFAConfig):
            raise ValueError("config должен быть экземпляром MFAConfig")

        return cls(config=config)
