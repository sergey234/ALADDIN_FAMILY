#!/usr/bin/env python3
"""
ALADDIN VPN - Two-Factor Authentication System
Система двухфакторной аутентификации для администраторов

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import base64
import hashlib
import hmac
import io
import json
import logging
import secrets
import smtplib
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pyotp
import qrcode

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Методы аутентификации"""

    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODE = "backup_code"
    PUSH = "push"  # Push уведомления


class AuthStatus(Enum):
    """Статусы аутентификации"""

    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    LOCKED = "locked"


@dataclass
class User2FA:
    """2FA настройки пользователя"""

    user_id: str
    enabled: bool = False
    methods: List[AuthMethod] = None
    totp_secret: Optional[str] = None
    backup_codes: List[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.backup_codes is None:
            self.backup_codes = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class AuthSession:
    """Сессия аутентификации"""

    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    verified: bool = False
    method_used: Optional[AuthMethod] = None
    device_fingerprint: Optional[str] = None

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at


class TwoFactorAuth:
    """
    Система двухфакторной аутентификации

    Функции:
    - TOTP (Google Authenticator, Authy)
    - SMS коды
    - Email коды
    - Backup коды
    - Push уведомления
    - IP whitelisting
    - Device fingerprinting
    - Session management
    """

    def __init__(self, config_file: str = "config/2fa_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Хранилища данных
        self.user_2fa: Dict[str, User2FA] = {}
        self.auth_sessions: Dict[str, AuthSession] = {}
        self.verification_codes: Dict[str, Dict[str, Any]] = {}

        # Настройки
        self.totp_issuer = (
            self.config.get("2fa_settings", {}).get("methods", {}).get("totp_app", {}).get("issuer", "ALADDIN VPN")
        )
        self.totp_algorithm = (
            self.config.get("2fa_settings", {}).get("methods", {}).get("totp_app", {}).get("algorithm", "SHA1")
        )
        self.totp_digits = self.config.get("2fa_settings", {}).get("methods", {}).get("totp_app", {}).get("digits", 6)
        self.totp_period = self.config.get("2fa_settings", {}).get("methods", {}).get("totp_app", {}).get("period", 30)

        # Безопасность
        self.max_attempts = self.config.get("2fa_settings", {}).get("security", {}).get("max_attempts", 3)
        self.lockout_duration = (
            self.config.get("2fa_settings", {}).get("security", {}).get("lockout_duration_minutes", 15)
        )
        self.code_expiry = self.config.get("2fa_settings", {}).get("security", {}).get("code_expiry_minutes", 5)
        self.remember_device_days = (
            self.config.get("2fa_settings", {}).get("security", {}).get("remember_device_days", 30)
        )

        logger.info("Two-Factor Authentication System initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "2fa_settings": {
                "enabled": True,
                "required_for": {
                    "admin_panel": True,
                    "vpn_connection": False,
                    "config_download": False,
                    "status_check": False,
                    "user_registration": False,
                },
                "methods": {
                    "sms": {"enabled": True, "provider": "twilio", "cost_per_sms": 0.01},
                    "email": {
                        "enabled": True,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "username": "",
                        "password": "",
                        "from_email": "noreply@aladdin-vpn.com",
                    },
                    "totp_app": {
                        "enabled": True,
                        "issuer": "ALADDIN VPN",
                        "algorithm": "SHA1",
                        "digits": 6,
                        "period": 30,
                    },
                    "backup_codes": {"enabled": True, "count": 10, "length": 8},
                },
                "security": {
                    "max_attempts": 3,
                    "lockout_duration_minutes": 15,
                    "code_expiry_minutes": 5,
                    "remember_device_days": 30,
                },
            }
        }

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        import os

        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _generate_secret(self) -> str:
        """Генерация секретного ключа для TOTP"""
        return pyotp.random_base32()

    def _generate_backup_codes(self, count: int = 10, length: int = 8) -> List[str]:
        """Генерация backup кодов"""
        codes = []
        for _ in range(count):
            code = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(length))
            codes.append(code)
        return codes

    def _generate_device_fingerprint(self, ip_address: str, user_agent: str) -> str:
        """Генерация отпечатка устройства"""
        fingerprint_data = f"{ip_address}:{user_agent}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    def setup_2fa(
        self, user_id: str, methods: List[AuthMethod], phone_number: str = None, email: str = None
    ) -> Dict[str, Any]:
        """
        Настройка 2FA для пользователя

        Args:
            user_id: ID пользователя
            methods: Список методов аутентификации
            phone_number: Номер телефона для SMS
            email: Email для кодов

        Returns:
            Dict с настройками 2FA
        """
        try:
            # Создаем или обновляем настройки 2FA
            if user_id not in self.user_2fa:
                self.user_2fa[user_id] = User2FA(user_id=user_id)

            user_2fa = self.user_2fa[user_id]
            user_2fa.enabled = True
            user_2fa.methods = methods
            user_2fa.phone_number = phone_number
            user_2fa.email = email

            result = {
                "user_id": user_id,
                "enabled": True,
                "methods": [method.value for method in methods],
                "setup_required": [],
            }

            # Настройка TOTP
            if AuthMethod.TOTP in methods:
                user_2fa.totp_secret = self._generate_secret()
                totp = pyotp.TOTP(user_2fa.totp_secret)

                # Генерируем QR код
                qr_data = totp.provisioning_uri(name=user_id, issuer_name=self.totp_issuer)

                result["totp"] = {
                    "secret": user_2fa.totp_secret,
                    "qr_code": self._generate_qr_code(qr_data),
                    "manual_entry_key": user_2fa.totp_secret,
                }
                result["setup_required"].append("totp")

            # Настройка backup кодов
            if AuthMethod.BACKUP_CODE in methods:
                user_2fa.backup_codes = self._generate_backup_codes()
                result["backup_codes"] = user_2fa.backup_codes
                result["setup_required"].append("backup_codes")

            # Настройка SMS
            if AuthMethod.SMS in methods and phone_number:
                result["sms"] = {"phone_number": phone_number, "verified": False}
                result["setup_required"].append("sms")

            # Настройка Email
            if AuthMethod.EMAIL in methods and email:
                result["email"] = {"email": email, "verified": False}
                result["setup_required"].append("email")

            logger.info(f"2FA setup completed for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error setting up 2FA for user {user_id}: {e}")
            return {"error": str(e)}

    def _generate_qr_code(self, data: str) -> str:
        """Генерация QR кода для TOTP"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Конвертируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return ""

    def verify_totp(self, user_id: str, code: str) -> Tuple[bool, str]:
        """Проверка TOTP кода"""
        try:
            if user_id not in self.user_2fa or not self.user_2fa[user_id].totp_secret:
                return False, "TOTP not configured"

            user_2fa = self.user_2fa[user_id]

            # Проверяем блокировку
            if self._is_user_locked(user_id):
                return False, "Account locked due to too many failed attempts"

            # Проверяем код
            totp = pyotp.TOTP(user_2fa.totp_secret)
            if totp.verify(code, valid_window=1):
                self._reset_failed_attempts(user_id)
                user_2fa.last_used = datetime.now(timezone.utc)
                return True, "TOTP verified successfully"
            else:
                self._increment_failed_attempts(user_id)
                return False, "Invalid TOTP code"

        except Exception as e:
            logger.error(f"Error verifying TOTP for user {user_id}: {e}")
            return False, "Verification error"

    def send_sms_code(self, user_id: str, phone_number: str) -> Tuple[bool, str]:
        """Отправка SMS кода"""
        try:
            if not self.config.get("2fa_settings", {}).get("methods", {}).get("sms", {}).get("enabled", True):
                return False, "SMS authentication disabled"

            # Генерируем код
            code = str(secrets.randbelow(1000000)).zfill(6)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.code_expiry)

            # Сохраняем код
            self.verification_codes[f"sms_{user_id}"] = {"code": code, "expires_at": expires_at, "attempts": 0}

            # Отправляем SMS (заглушка)
            logger.info(f"SMS code for user {user_id}: {code}")

            return True, "SMS code sent successfully"

        except Exception as e:
            logger.error(f"Error sending SMS code for user {user_id}: {e}")
            return False, "Failed to send SMS code"

    def send_email_code(self, user_id: str, email: str) -> Tuple[bool, str]:
        """Отправка email кода"""
        try:
            if not self.config.get("2fa_settings", {}).get("methods", {}).get("email", {}).get("enabled", True):
                return False, "Email authentication disabled"

            # Генерируем код
            code = str(secrets.randbelow(1000000)).zfill(6)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.code_expiry)

            # Сохраняем код
            self.verification_codes[f"email_{user_id}"] = {"code": code, "expires_at": expires_at, "attempts": 0}

            # Отправляем email (заглушка)
            logger.info(f"Email code for user {user_id}: {code}")

            return True, "Email code sent successfully"

        except Exception as e:
            logger.error(f"Error sending email code for user {user_id}: {e}")
            return False, "Failed to send email code"

    def verify_code(self, user_id: str, code: str, method: AuthMethod) -> Tuple[bool, str]:
        """Проверка кода аутентификации"""
        try:
            if self._is_user_locked(user_id):
                return False, "Account locked due to too many failed attempts"

            if method == AuthMethod.TOTP:
                return self.verify_totp(user_id, code)
            elif method == AuthMethod.BACKUP_CODE:
                return self.verify_backup_code(user_id, code)
            elif method in [AuthMethod.SMS, AuthMethod.EMAIL]:
                return self._verify_verification_code(user_id, code, method)
            else:
                return False, "Unsupported authentication method"

        except Exception as e:
            logger.error(f"Error verifying code for user {user_id}: {e}")
            return False, "Verification error"

    def verify_backup_code(self, user_id: str, code: str) -> Tuple[bool, str]:
        """Проверка backup кода"""
        try:
            if user_id not in self.user_2fa:
                return False, "User not found"

            user_2fa = self.user_2fa[user_id]

            if code in user_2fa.backup_codes:
                # Удаляем использованный код
                user_2fa.backup_codes.remove(code)
                self._reset_failed_attempts(user_id)
                user_2fa.last_used = datetime.now(timezone.utc)
                return True, "Backup code verified successfully"
            else:
                self._increment_failed_attempts(user_id)
                return False, "Invalid backup code"

        except Exception as e:
            logger.error(f"Error verifying backup code for user {user_id}: {e}")
            return False, "Verification error"

    def _verify_verification_code(self, user_id: str, code: str, method: AuthMethod) -> Tuple[bool, str]:
        """Проверка SMS/Email кода"""
        try:
            key = f"{method.value}_{user_id}"

            if key not in self.verification_codes:
                return False, "No verification code found"

            verification_data = self.verification_codes[key]

            # Проверяем срок действия
            if datetime.now(timezone.utc) > verification_data["expires_at"]:
                del self.verification_codes[key]
                return False, "Verification code expired"

            # Проверяем количество попыток
            if verification_data["attempts"] >= self.max_attempts:
                del self.verification_codes[key]
                self._increment_failed_attempts(user_id)
                return False, "Too many verification attempts"

            # Проверяем код
            if verification_data["code"] == code:
                del self.verification_codes[key]
                self._reset_failed_attempts(user_id)
                if user_id in self.user_2fa:
                    self.user_2fa[user_id].last_used = datetime.now(timezone.utc)
                return True, f"{method.value.upper()} code verified successfully"
            else:
                verification_data["attempts"] += 1
                return False, f"Invalid {method.value} code"

        except Exception as e:
            logger.error(f"Error verifying {method.value} code for user {user_id}: {e}")
            return False, "Verification error"

    def create_auth_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Создание сессии аутентификации"""
        try:
            session_id = secrets.token_urlsafe(32)
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=self.remember_device_days)

            device_fingerprint = self._generate_device_fingerprint(ip_address, user_agent)

            session = AuthSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=now,
                expires_at=expires_at,
                device_fingerprint=device_fingerprint,
            )

            self.auth_sessions[session_id] = session

            logger.info(f"Auth session created for user {user_id}")
            return session_id

        except Exception as e:
            logger.error(f"Error creating auth session for user {user_id}: {e}")
            return ""

    def verify_session(
        self, session_id: str, ip_address: str = None, user_agent: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Проверка сессии аутентификации"""
        try:
            if session_id not in self.auth_sessions:
                return False, "Session not found", None

            session = self.auth_sessions[session_id]

            # Проверяем срок действия
            if session.is_expired():
                del self.auth_sessions[session_id]
                return False, "Session expired", None

            # Проверяем IP и User-Agent (опционально)
            if ip_address and session.ip_address != ip_address:
                return False, "IP address mismatch", None

            if user_agent and session.user_agent != user_agent:
                return False, "User agent mismatch", None

            return True, "Session valid", session.user_id

        except Exception as e:
            logger.error(f"Error verifying session {session_id}: {e}")
            return False, "Session verification error", None

    def _is_user_locked(self, user_id: str) -> bool:
        """Проверка блокировки пользователя"""
        if user_id not in self.user_2fa:
            return False

        user_2fa = self.user_2fa[user_id]

        if user_2fa.locked_until and datetime.now(timezone.utc) < user_2fa.locked_until:
            return True

        return False

    def _increment_failed_attempts(self, user_id: str) -> None:
        """Увеличение счетчика неудачных попыток"""
        if user_id not in self.user_2fa:
            self.user_2fa[user_id] = User2FA(user_id=user_id)

        user_2fa = self.user_2fa[user_id]
        user_2fa.failed_attempts += 1

        if user_2fa.failed_attempts >= self.max_attempts:
            user_2fa.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.lockout_duration)
            logger.warning(f"User {user_id} locked due to {user_2fa.failed_attempts} failed attempts")

    def _reset_failed_attempts(self, user_id: str) -> None:
        """Сброс счетчика неудачных попыток"""
        if user_id in self.user_2fa:
            self.user_2fa[user_id].failed_attempts = 0
            self.user_2fa[user_id].locked_until = None

    def is_2fa_required(self, endpoint: str) -> bool:
        """Проверка необходимости 2FA для эндпоинта"""
        required_for = self.config.get("2fa_settings", {}).get("required_for", {})

        if "/admin" in endpoint:
            return required_for.get("admin_panel", True)
        elif "/vpn/connect" in endpoint:
            return required_for.get("vpn_connection", False)
        elif "/config" in endpoint:
            return required_for.get("config_download", False)
        elif "/status" in endpoint:
            return required_for.get("status_check", False)
        elif "/register" in endpoint:
            return required_for.get("user_registration", False)

        return False

    def get_user_2fa_status(self, user_id: str) -> Dict[str, Any]:
        """Получение статуса 2FA пользователя"""
        if user_id not in self.user_2fa:
            return {"enabled": False, "methods": [], "setup_required": True}

        user_2fa = self.user_2fa[user_id]

        return {
            "enabled": user_2fa.enabled,
            "methods": [method.value for method in user_2fa.methods],
            "has_totp": user_2fa.totp_secret is not None,
            "has_backup_codes": len(user_2fa.backup_codes) > 0,
            "has_sms": user_2fa.phone_number is not None,
            "has_email": user_2fa.email is not None,
            "failed_attempts": user_2fa.failed_attempts,
            "locked_until": user_2fa.locked_until.isoformat() if user_2fa.locked_until else None,
            "last_used": user_2fa.last_used.isoformat() if user_2fa.last_used else None,
        }

    def cleanup_expired_sessions(self) -> None:
        """Очистка истекших сессий"""
        expired_sessions = [session_id for session_id, session in self.auth_sessions.items() if session.is_expired()]

        for session_id in expired_sessions:
            del self.auth_sessions[session_id]

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики 2FA"""
        total_users = len(self.user_2fa)
        enabled_users = len([u for u in self.user_2fa.values() if u.enabled])
        active_sessions = len([s for s in self.auth_sessions.values() if not s.is_expired()])

        return {
            "total_users": total_users,
            "enabled_2fa": enabled_users,
            "active_sessions": active_sessions,
            "pending_verifications": len(self.verification_codes),
            "locked_users": len(
                [u for u in self.user_2fa.values() if u.locked_until and u.locked_until > datetime.now(timezone.utc)]
            ),
        }


# Глобальный экземпляр 2FA системы
two_factor_auth = TwoFactorAuth()


def setup_user_2fa(user_id: str, methods: List[AuthMethod], **kwargs) -> Dict[str, Any]:
    """Глобальная функция настройки 2FA"""
    return two_factor_auth.setup_2fa(user_id, methods, **kwargs)


def verify_2fa_code(user_id: str, code: str, method: AuthMethod) -> Tuple[bool, str]:
    """Глобальная функция проверки 2FA кода"""
    return two_factor_auth.verify_code(user_id, code, method)


def is_2fa_required(endpoint: str) -> bool:
    """Проверка необходимости 2FA для эндпоинта"""
    return two_factor_auth.is_2fa_required(endpoint)


if __name__ == "__main__":
    # Тестирование системы 2FA
    print("🧪 Testing Two-Factor Authentication System...")

    # Настройка 2FA для тестового пользователя
    user_id = "admin_test"
    methods = [AuthMethod.TOTP, AuthMethod.BACKUP_CODE, AuthMethod.EMAIL]

    setup_result = setup_user_2fa(user_id=user_id, methods=methods, email="admin@aladdin-vpn.com")

    print(f"2FA Setup: {json.dumps(setup_result, indent=2)}")

    # Тест проверки эндпоинтов
    test_endpoints = ["/admin/dashboard", "/vpn/connect", "/api/status", "/config/download"]

    for endpoint in test_endpoints:
        required = is_2fa_required(endpoint)
        print(f"Endpoint {endpoint}: 2FA required = {required}")

    # Статистика
    stats = two_factor_auth.get_statistics()
    print(f"\n📊 Statistics: {json.dumps(stats, indent=2)}")

    print("✅ Two-Factor Authentication System test completed")
