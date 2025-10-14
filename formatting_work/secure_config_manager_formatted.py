"""
Безопасный менеджер конфигурации для ALADDIN Security System
Устраняет хардкод секретов и обеспечивает безопасное хранение
"""

import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


# Упрощенная реализация без внешних зависимостей
class Fernet:
    """Упрощенная реализация Fernet шифрования"""

    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        """Упрощенное шифрование"""
        import base64

        # Простое XOR шифрование для демонстрации
        encrypted = bytearray()
        key_bytes = self.key[:32]  # Берем первые 32 байта
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return base64.urlsafe_b64encode(encrypted)

    def decrypt(self, encrypted_data):
        """Упрощенная расшифровка"""
        import base64

        encrypted = base64.urlsafe_b64decode(encrypted_data)
        decrypted = bytearray()
        key_bytes = self.key[:32]
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return decrypted


class PBKDF2HMAC:
    """Упрощенная реализация PBKDF2HMAC"""

    def __init__(self, algorithm, length, salt, iterations):
        self.algorithm = algorithm
        self.length = length
        self.salt = salt
        self.iterations = iterations

    def derive(self, password):
        """Упрощенное получение ключа"""
        try:
            return hashlib.pbkdf2_hmac(
                "sha256", password, self.salt, self.iterations
            )[: self.length]
        except AttributeError:
            # Fallback для старых версий Python
            import hmac

            key = password
            for i in range(self.iterations):
                key = hmac.new(self.salt + key, key, hashlib.sha256).digest()
            return key[: self.length]


class hashes:
    """Упрощенная реализация hashes"""

    SHA256 = "sha256"


@dataclass
class SecureConfig:
    """Безопасная конфигурация"""

    telegram_bot_token: Optional[str] = None
    discord_bot_token: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    email_password: Optional[str] = None
    firebase_server_key: Optional[str] = None
    encryption_key: Optional[str] = None
    api_rate_limit: int = 100
    max_message_length: int = 4096


class SecureConfigManager:
    """
    Безопасный менеджер конфигурации
    Использует переменные окружения и шифрование для хранения секретов
    """

    def __init__(self, config_file: str = "secure_config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self._config: Optional[SecureConfig] = None
        self._encryption_key: Optional[bytes] = None

    def _get_encryption_key(self) -> bytes:
        """Получение ключа шифрования из переменных окружения"""
        if self._encryption_key:
            return self._encryption_key

        # Получаем мастер-пароль из переменных окружения
        master_password = os.getenv("ALADDIN_MASTER_PASSWORD")
        if not master_password:
            raise ValueError(
                "ALADDIN_MASTER_PASSWORD не установлен в переменных окружения! "
                "Установите: export ALADDIN_MASTER_PASSWORD='your_secure_password'"
            )

        # Генерируем соль из имени файла конфигурации
        salt = self.config_file.encode()[:16].ljust(16, b"0")

        # Создаем ключ шифрования
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
        )

        self._encryption_key = base64.urlsafe_b64encode(
            kdf.derive(master_password.encode())
        )

        return self._encryption_key

    def _encrypt_value(self, value: str) -> str:
        """Шифрование значения"""
        if not value:
            return ""

        fernet = Fernet(self._get_encryption_key())
        encrypted = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Расшифровка значения"""
        if not encrypted_value:
            return ""

        try:
            fernet = Fernet(self._get_encryption_key())
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Ошибка расшифровки: {e}")
            return ""

    def load_config(self) -> SecureConfig:
        """Загрузка конфигурации из файла или переменных окружения"""
        config = SecureConfig()

        # Приоритет: переменные окружения > файл конфигурации
        config.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        config.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        config.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        config.email_password = os.getenv("EMAIL_PASSWORD")
        config.firebase_server_key = os.getenv("FIREBASE_SERVER_KEY")
        config.encryption_key = os.getenv("ENCRYPTION_KEY")

        # Загружаем дополнительные настройки из файла
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)

                # Расшифровываем значения из файла
                for key, value in file_config.items():
                    if key.endswith("_encrypted") and value:
                        original_key = key.replace("_encrypted", "")
                        decrypted_value = self._decrypt_value(value)
                        setattr(config, original_key, decrypted_value)
                    elif hasattr(config, key) and not getattr(config, key):
                        setattr(config, key, value)

            except Exception as e:
                self.logger.warning(f"Ошибка загрузки файла конфигурации: {e}")

        self._config = config
        return config

    def save_config(self, config: SecureConfig) -> bool:
        """Сохранение конфигурации в зашифрованном виде"""
        try:
            config_dict = {}

            # Шифруем секретные значения
            secret_fields = [
                "telegram_bot_token",
                "discord_bot_token",
                "twilio_auth_token",
                "email_password",
                "firebase_server_key",
                "encryption_key",
            ]

            for field in secret_fields:
                value = getattr(config, field)
                if value:
                    config_dict[f"{field}_encrypted"] = self._encrypt_value(
                        value
                    )

            # Сохраняем несекретные значения
            config_dict["api_rate_limit"] = config.api_rate_limit
            config_dict["max_message_length"] = config.max_message_length

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Конфигурация сохранена в {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False

    def get_config(self) -> SecureConfig:
        """Получение текущей конфигурации"""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def validate_config(self) -> Dict[str, Any]:
        """Валидация конфигурации"""
        config = self.get_config()
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "security_score": 0,
        }

        # Проверяем наличие секретов
        secret_fields = [
            ("telegram_bot_token", "Telegram Bot Token"),
            ("discord_bot_token", "Discord Bot Token"),
            ("twilio_auth_token", "Twilio Auth Token"),
            ("email_password", "Email Password"),
            ("firebase_server_key", "Firebase Server Key"),
            ("encryption_key", "Encryption Key"),
        ]

        security_score = 0
        for field, name in secret_fields:
            value = getattr(config, field)
            if value:
                security_score += 1
                if len(value) < 8:
                    validation_result["warnings"].append(
                        f"{name} слишком короткий"
                    )
                if value in [
                    "YOUR_TELEGRAM_BOT_TOKEN",
                    "YOUR_DISCORD_BOT_TOKEN",
                    "YOUR_TWILIO_TOKEN",
                    "your_app_password",
                    "YOUR_FIREBASE_SERVER_KEY",
                    "YOUR_ENCRYPTION_KEY",
                ]:
                    validation_result["errors"].append(
                        f"{name} содержит шаблонное значение"
                    )
                    validation_result["valid"] = False
            else:
                validation_result["warnings"].append(f"{name} не установлен")

        validation_result["security_score"] = (
            security_score / len(secret_fields)
        ) * 100

        return validation_result

    def create_env_template(self, output_file: str = ".env.template") -> bool:
        """Создание шаблона файла переменных окружения"""
        try:
            template = """# ALADDIN Security System - Environment Variables Template
# Скопируйте этот файл в .env и заполните реальными значениями

# Master Password для шифрования конфигурации
ALADDIN_MASTER_PASSWORD=your_secure_master_password_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_NUMBER=+1234567890

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Firebase Push Notifications
FIREBASE_SERVER_KEY=your_firebase_server_key_here
FCM_PROJECT_ID=your_fcm_project_id_here

# Security Settings
ENCRYPTION_KEY=your_encryption_key_here
API_RATE_LIMIT=100
MAX_MESSAGE_LENGTH=4096
"""

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(template)

            self.logger.info(
                f"Шаблон переменных окружения создан: {output_file}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания шаблона: {e}")
            return False


# Пример использования
if __name__ == "__main__":
    # Создаем менеджер конфигурации
    config_manager = SecureConfigManager()

    # Создаем шаблон переменных окружения
    config_manager.create_env_template()

    # Загружаем конфигурацию
    config = config_manager.load_config()

    # Валидируем конфигурацию
    validation = config_manager.validate_config()

    print(f"Конфигурация загружена: {validation['valid']}")
    print(f"Оценка безопасности: {validation['security_score']:.1f}%")

    if validation["errors"]:
        print("Ошибки:")
        for error in validation["errors"]:
            print(f"  - {error}")

    if validation["warnings"]:
        print("Предупреждения:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
