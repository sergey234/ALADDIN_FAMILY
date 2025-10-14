#!/usr/bin/env python3
"""
ALADDIN Security System - Secrets Integration
Интеграция SecretsManager с существующими компонентами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-26
"""

import json
from pathlib import Path
from typing import Any, Dict

from core.security_base import ComponentStatus, SecurityBase
from security.secrets_api import get_secrets_api
from security.secrets_manager import get_secrets_manager


class SecretsIntegration(SecurityBase):
    """Интеграция секретов с существующими компонентами"""

    def __init__(self):
        """Инициализация интеграции"""
        super().__init__("SecretsIntegration")
        self.secrets_manager = get_secrets_manager()
        self.secrets_api = get_secrets_api()
        self.integration_config = {}
        self.log_activity("SecretsIntegration инициализирован")

    def initialize(self) -> bool:
        """Инициализация интеграции"""
        try:
            self.log_activity("Инициализация интеграции секретов...")

            # Загрузка конфигурации интеграции
            self._load_integration_config()

            # Интеграция с существующими компонентами
            self._integrate_with_existing_components()

            # Миграция существующих секретов
            self._migrate_existing_secrets()

            self.status = ComponentStatus.RUNNING
            self.log_activity("Интеграция секретов завершена успешно")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации интеграции: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _load_integration_config(self) -> None:
        """Загрузка конфигурации интеграции"""
        try:
            config_file = Path("config/secrets_integration.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    self.integration_config = json.load(f)
            else:
                # Создание конфигурации по умолчанию
                self.integration_config = {
                    "migrate_existing": True,
                    "auto_backup": True,
                    "components": {
                        "password_security_agent": {
                            "enabled": True,
                            "secret_prefix": "password_agent_",
                            "migrate_passwords": True,
                        },
                        "api_gateway": {
                            "enabled": True,
                            "secret_prefix": "api_gateway_",
                            "migrate_tokens": True,
                        },
                        "authentication_manager": {
                            "enabled": True,
                            "secret_prefix": "auth_manager_",
                            "migrate_credentials": True,
                        },
                        "secure_config_manager": {
                            "enabled": True,
                            "secret_prefix": "config_manager_",
                            "migrate_configs": True,
                        },
                    },
                }
                self._save_integration_config()

            self.log_activity("Конфигурация интеграции загружена")

        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки конфигурации интеграции: {e}", "error"
            )

    def _save_integration_config(self) -> None:
        """Сохранение конфигурации интеграции"""
        try:
            config_file = Path("config/secrets_integration.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.integration_config, f, ensure_ascii=False, indent=2
                )

        except Exception as e:
            self.log_activity(
                f"Ошибка сохранения конфигурации интеграции: {e}", "error"
            )

    def _integrate_with_existing_components(self) -> None:
        """Интеграция с существующими компонентами"""
        try:
            components_config = self.integration_config.get("components", {})

            for component_name, config in components_config.items():
                if config.get("enabled", False):
                    self._integrate_component(component_name, config)

        except Exception as e:
            self.log_activity(
                f"Ошибка интеграции с компонентами: {e}", "error"
            )

    def _integrate_component(
        self, component_name: str, config: Dict[str, Any]
    ) -> None:
        """Интеграция с конкретным компонентом"""
        try:
            self.log_activity(f"Интеграция с компонентом: {component_name}")

            if component_name == "password_security_agent":
                self._integrate_password_security_agent(config)
            elif component_name == "api_gateway":
                self._integrate_api_gateway(config)
            elif component_name == "authentication_manager":
                self._integrate_authentication_manager(config)
            elif component_name == "secure_config_manager":
                self._integrate_secure_config_manager(config)
            else:
                self.log_activity(
                    f"Неизвестный компонент для интеграции: {component_name}",
                    "warning",
                )

        except Exception as e:
            self.log_activity(
                f"Ошибка интеграции с {component_name}: {e}", "error"
            )

    def _integrate_password_security_agent(
        self, config: Dict[str, Any]
    ) -> None:
        """Интеграция с PasswordSecurityAgent"""
        try:
            # Поиск файла PasswordSecurityAgent
            agent_file = Path("security/ai_agents/password_security_agent.py")
            if not agent_file.exists():
                self.log_activity("PasswordSecurityAgent не найден", "warning")
                return

            # Создание адаптера для PasswordSecurityAgent
            adapter_code = '''
# Адаптер для интеграции с SecretsManager
from security.secrets_api import get_secrets_api

class PasswordSecurityAgentSecretsAdapter:
    """Адаптер для интеграции PasswordSecurityAgent с SecretsManager"""

    def __init__(self):
        self.secrets_api = get_secrets_api()
        self.secret_prefix = "password_agent_"

    def store_password_hash(self, user_id: str, password_hash: str) -> bool:
        """Сохранение хеша пароля в SecretsManager"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}hash_{user_id}",
                value=password_hash,
                secret_type="password",
                description=f"Хеш пароля пользователя {user_id}",
                tags={"component": "password_security_agent", "user_id": user_id}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_password_hash(self, user_id: str) -> Optional[str]:
        """Получение хеша пароля из SecretsManager"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}hash_{user_id}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def rotate_password_hash(self, user_id: str, new_hash: str) -> bool:
        """Ротация хеша пароля"""
        try:
            result = self.secrets_api.rotate_secret(
                f"{self.secret_prefix}hash_{user_id}",
                new_value=new_hash,
                by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False

    def delete_password_hash(self, user_id: str) -> bool:
        """Удаление хеша пароля"""
        try:
            result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}hash_{user_id}", by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False
'''

            # Сохранение адаптера
            adapter_file = Path(
                "security/adapters/password_security_agent_secrets_adapter.py"
            )
            adapter_file.parent.mkdir(parents=True, exist_ok=True)

            with open(adapter_file, "w", encoding="utf-8") as f:
                f.write(adapter_code)

            self.log_activity("Адаптер для PasswordSecurityAgent создан")

        except Exception as e:
            self.log_activity(
                f"Ошибка интеграции с PasswordSecurityAgent: {e}", "error"
            )

    def _integrate_api_gateway(self, config: Dict[str, Any]) -> None:
        """Интеграция с API Gateway"""
        try:
            # Создание адаптера для API Gateway
            adapter_code = '''
# Адаптер для интеграции API Gateway с SecretsManager
from security.secrets_api import get_secrets_api
from typing import Optional, Dict, Any

class APIGatewaySecretsAdapter:
    """Адаптер для интеграции API Gateway с SecretsManager"""

    def __init__(self):
        self.secrets_api = get_secrets_api()
        self.secret_prefix = "api_gateway_"

    def store_api_key(self, service_name: str, api_key: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Сохранение API ключа"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}key_{service_name}",
                value=api_key,
                secret_type="api_key",
                description=f"API ключ для сервиса {service_name}",
                tags={"component": "api_gateway", "service": service_name}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_api_key(self, service_name: str) -> Optional[str]:
        """Получение API ключа"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}key_{service_name}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def store_jwt_token(self, user_id: str, token: str, expires_at: Optional[str] = None) -> bool:
        """Сохранение JWT токена"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}jwt_{user_id}",
                value=token,
                secret_type="jwt_token",
                description=f"JWT токен пользователя {user_id}",
                tags={"component": "api_gateway", "user_id": user_id}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_jwt_token(self, user_id: str) -> Optional[str]:
        """Получение JWT токена"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}jwt_{user_id}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def rotate_api_key(self, service_name: str, new_key: str) -> bool:
        """Ротация API ключа"""
        try:
            result = self.secrets_api.rotate_secret(
                f"{self.secret_prefix}key_{service_name}",
                new_value=new_key,
                by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False

    def delete_api_key(self, service_name: str) -> bool:
        """Удаление API ключа"""
        try:
            result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}key_{service_name}", by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False
'''

            # Сохранение адаптера
            adapter_file = Path(
                "security/adapters/api_gateway_secrets_adapter.py"
            )
            adapter_file.parent.mkdir(parents=True, exist_ok=True)

            with open(adapter_file, "w", encoding="utf-8") as f:
                f.write(adapter_code)

            self.log_activity("Адаптер для API Gateway создан")

        except Exception as e:
            self.log_activity(f"Ошибка интеграции с API Gateway: {e}", "error")

    def _integrate_authentication_manager(
        self, config: Dict[str, Any]
    ) -> None:
        """Интеграция с AuthenticationManager"""
        try:
            # Создание адаптера для AuthenticationManager
            adapter_code = '''
# Адаптер для интеграции AuthenticationManager с SecretsManager
from security.secrets_api import get_secrets_api
from typing import Optional, Dict, Any

class AuthenticationManagerSecretsAdapter:
    """Адаптер для интеграции AuthenticationManager с SecretsManager"""

    def __init__(self):
        self.secrets_api = get_secrets_api()
        self.secret_prefix = "auth_manager_"

    def store_user_credentials(self, user_id: str, username: str, password_hash: str) -> bool:
        """Сохранение учетных данных пользователя"""
        try:
            # Сохранение хеша пароля
            password_result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}password_{user_id}",
                value=password_hash,
                secret_type="password",
                description=f"Хеш пароля пользователя {username}",
                tags={"component": "authentication_manager", "user_id": user_id, "username": username}
            )

            # Сохранение имени пользователя
            username_result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}username_{user_id}",
                value=username,
                secret_type="custom",
                description=f"Имя пользователя {user_id}",
                tags={"component": "authentication_manager", "user_id": user_id}
            )

            return password_result.get("success", False) and username_result.get("success", False)
        except Exception:
            return False

    def get_user_credentials(self, user_id: str) -> Optional[Dict[str, str]]:
        """Получение учетных данных пользователя"""
        try:
            # Получение хеша пароля
            password_result = self.secrets_api.get_secret(
                f"{self.secret_prefix}password_{user_id}", by_name=True
            )

            # Получение имени пользователя
            username_result = self.secrets_api.get_secret(
                f"{self.secret_prefix}username_{user_id}", by_name=True
            )

            if password_result.get("success") and username_result.get("success"):
                return {
                    "username": username_result.get("value"),
                    "password_hash": password_result.get("value")
                }
            return None
        except Exception:
            return None

    def store_session_token(self, user_id: str, session_token: str, expires_at: Optional[str] = None) -> bool:
        """Сохранение токена сессии"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}session_{user_id}",
                value=session_token,
                secret_type="jwt_token",
                description=f"Токен сессии пользователя {user_id}",
                tags={"component": "authentication_manager", "user_id": user_id}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_session_token(self, user_id: str) -> Optional[str]:
        """Получение токена сессии"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}session_{user_id}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def delete_user_credentials(self, user_id: str) -> bool:
        """Удаление учетных данных пользователя"""
        try:
            # Удаление хеша пароля
            password_result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}password_{user_id}", by_name=True
            )

            # Удаление имени пользователя
            username_result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}username_{user_id}", by_name=True
            )

            # Удаление токена сессии
            session_result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}session_{user_id}", by_name=True
            )

            return (password_result.get("success", False) and
                    username_result.get("success", False) and
                    session_result.get("success", False))
        except Exception:
            return False
'''

            # Сохранение адаптера
            adapter_file = Path(
                "security/adapters/authentication_manager_secrets_adapter.py"
            )
            adapter_file.parent.mkdir(parents=True, exist_ok=True)

            with open(adapter_file, "w", encoding="utf-8") as f:
                f.write(adapter_code)

            self.log_activity("Адаптер для AuthenticationManager создан")

        except Exception as e:
            self.log_activity(
                f"Ошибка интеграции с AuthenticationManager: {e}", "error"
            )

    def _integrate_secure_config_manager(self, config: Dict[str, Any]) -> None:
        """Интеграция с SecureConfigManager"""
        try:
            # Создание адаптера для SecureConfigManager
            adapter_code = '''
# Адаптер для интеграции SecureConfigManager с SecretsManager
from security.secrets_api import get_secrets_api
from typing import Optional, Dict, Any

class SecureConfigManagerSecretsAdapter:
    """Адаптер для интеграции SecureConfigManager с SecretsManager"""

    def __init__(self):
        self.secrets_api = get_secrets_api()
        self.secret_prefix = "config_manager_"

    def store_config_secret(self, config_key: str, config_value: str, description: Optional[str] = None) -> bool:
        """Сохранение конфигурационного секрета"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}{config_key}",
                value=config_value,
                secret_type="config_secret",
                description=description or f"Конфигурационный секрет {config_key}",
                tags={"component": "secure_config_manager", "config_key": config_key}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_config_secret(self, config_key: str) -> Optional[str]:
        """Получение конфигурационного секрета"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}{config_key}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def store_database_credentials(self, db_name: str, username: str, password: str, host: str, port: int) -> bool:
        """Сохранение учетных данных базы данных"""
        try:
            credentials = {
                "username": username,
                "password": password,
                "host": host,
                "port": port
            }

            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}db_{db_name}",
                value=json.dumps(credentials),
                secret_type="database_credentials",
                description=f"Учетные данные базы данных {db_name}",
                tags={"component": "secure_config_manager", "database": db_name}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_database_credentials(self, db_name: str) -> Optional[Dict[str, Any]]:
        """Получение учетных данных базы данных"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}db_{db_name}", by_name=True
            )
            if result.get("success"):
                credentials_json = result.get("value")
                return json.loads(credentials_json)
            return None
        except Exception:
            return None

    def store_encryption_key(self, key_name: str, encryption_key: str) -> bool:
        """Сохранение ключа шифрования"""
        try:
            result = self.secrets_api.create_secret(
                name=f"{self.secret_prefix}encryption_{key_name}",
                value=encryption_key,
                secret_type="encryption_key",
                description=f"Ключ шифрования {key_name}",
                tags={"component": "secure_config_manager", "key_name": key_name}
            )
            return result.get("success", False)
        except Exception:
            return False

    def get_encryption_key(self, key_name: str) -> Optional[str]:
        """Получение ключа шифрования"""
        try:
            result = self.secrets_api.get_secret(
                f"{self.secret_prefix}encryption_{key_name}", by_name=True
            )
            if result.get("success"):
                return result.get("value")
            return None
        except Exception:
            return None

    def rotate_config_secret(self, config_key: str, new_value: str) -> bool:
        """Ротация конфигурационного секрета"""
        try:
            result = self.secrets_api.rotate_secret(
                f"{self.secret_prefix}{config_key}",
                new_value=new_value,
                by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False

    def delete_config_secret(self, config_key: str) -> bool:
        """Удаление конфигурационного секрета"""
        try:
            result = self.secrets_api.delete_secret(
                f"{self.secret_prefix}{config_key}", by_name=True
            )
            return result.get("success", False)
        except Exception:
            return False
'''

            # Сохранение адаптера
            adapter_file = Path(
                "security/adapters/secure_config_manager_secrets_adapter.py"
            )
            adapter_file.parent.mkdir(parents=True, exist_ok=True)

            with open(adapter_file, "w", encoding="utf-8") as f:
                f.write(adapter_code)

            self.log_activity("Адаптер для SecureConfigManager создан")

        except Exception as e:
            self.log_activity(
                f"Ошибка интеграции с SecureConfigManager: {e}", "error"
            )

    def _migrate_existing_secrets(self) -> None:
        """Миграция существующих секретов"""
        try:
            if not self.integration_config.get("migrate_existing", True):
                self.log_activity("Миграция существующих секретов отключена")
                return

            self.log_activity("Начало миграции существующих секретов...")

            # Миграция секретов из различных источников
            self._migrate_from_config_files()
            self._migrate_from_environment_variables()
            self._migrate_from_database()

            self.log_activity("Миграция существующих секретов завершена")

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции существующих секретов: {e}", "error"
            )

    def _migrate_from_config_files(self) -> None:
        """Миграция секретов из конфигурационных файлов"""
        try:
            # Поиск конфигурационных файлов с секретами
            config_files = [
                "config/database.json",
                "config/api_keys.json",
                "config/encryption_keys.json",
                "config/passwords.json",
            ]

            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    self._migrate_config_file(config_path)

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции из конфигурационных файлов: {e}", "error"
            )

    def _migrate_config_file(self, config_path: Path) -> None:
        """Миграция секретов из конкретного конфигурационного файла"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Определение типа секретов по имени файла
            if "database" in config_path.name:
                self._migrate_database_config(config_data)
            elif "api_keys" in config_path.name:
                self._migrate_api_keys_config(config_data)
            elif "encryption_keys" in config_path.name:
                self._migrate_encryption_keys_config(config_data)
            elif "passwords" in config_path.name:
                self._migrate_passwords_config(config_data)

            self.log_activity(f"Миграция из {config_path} завершена")

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции из {config_path}: {e}", "error"
            )

    def _migrate_database_config(self, config_data: Dict[str, Any]) -> None:
        """Миграция конфигурации базы данных"""
        try:
            for db_name, db_config in config_data.items():
                if isinstance(db_config, dict) and "password" in db_config:
                    # Сохранение учетных данных БД
                    result = self.secrets_api.create_secret(
                        name=f"migrated_db_{db_name}",
                        value=json.dumps(db_config),
                        secret_type="database_credentials",
                        description=f"Мигрированные учетные данные БД {db_name}",
                        tags={
                            "migrated": "true",
                            "source": "config_file",
                            "database": db_name,
                        },
                    )

                    if result.get("success"):
                        self.log_activity(
                            f"Мигрированы учетные данные БД: {db_name}"
                        )

        except Exception as e:
            self.log_activity(f"Ошибка миграции конфигурации БД: {e}", "error")

    def _migrate_api_keys_config(self, config_data: Dict[str, Any]) -> None:
        """Миграция API ключей"""
        try:
            for service_name, api_key in config_data.items():
                if isinstance(api_key, str):
                    result = self.secrets_api.create_secret(
                        name=f"migrated_api_key_{service_name}",
                        value=api_key,
                        secret_type="api_key",
                        description=f"Мигрированный API ключ для {service_name}",
                        tags={
                            "migrated": "true",
                            "source": "config_file",
                            "service": service_name,
                        },
                    )

                    if result.get("success"):
                        self.log_activity(
                            f"Мигрирован API ключ: {service_name}"
                        )

        except Exception as e:
            self.log_activity(f"Ошибка миграции API ключей: {e}", "error")

    def _migrate_encryption_keys_config(
        self, config_data: Dict[str, Any]
    ) -> None:
        """Миграция ключей шифрования"""
        try:
            for key_name, key_value in config_data.items():
                if isinstance(key_value, str):
                    result = self.secrets_api.create_secret(
                        name=f"migrated_encryption_key_{key_name}",
                        value=key_value,
                        secret_type="encryption_key",
                        description=f"Мигрированный ключ шифрования {key_name}",
                        tags={
                            "migrated": "true",
                            "source": "config_file",
                            "key_name": key_name,
                        },
                    )

                    if result.get("success"):
                        self.log_activity(
                            f"Мигрирован ключ шифрования: {key_name}"
                        )

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции ключей шифрования: {e}", "error"
            )

    def _migrate_passwords_config(self, config_data: Dict[str, Any]) -> None:
        """Миграция паролей"""
        try:
            for user_id, password_data in config_data.items():
                if (
                    isinstance(password_data, dict)
                    and "password" in password_data
                ):
                    result = self.secrets_api.create_secret(
                        name=f"migrated_password_{user_id}",
                        value=password_data["password"],
                        secret_type="password",
                        description=f"Мигрированный пароль пользователя {user_id}",
                        tags={
                            "migrated": "true",
                            "source": "config_file",
                            "user_id": user_id,
                        },
                    )

                    if result.get("success"):
                        self.log_activity(f"Мигрирован пароль: {user_id}")

        except Exception as e:
            self.log_activity(f"Ошибка миграции паролей: {e}", "error")

    def _migrate_from_environment_variables(self) -> None:
        """Миграция секретов из переменных окружения"""
        try:
            import os

            # Список переменных окружения для миграции
            env_vars = [
                "DATABASE_PASSWORD",
                "API_KEY",
                "JWT_SECRET",
                "ENCRYPTION_KEY",
                "REDIS_PASSWORD",
            ]

            for env_var in env_vars:
                env_value = os.getenv(env_var)
                if env_value:
                    # Определение типа секрета
                    secret_type = "custom"
                    if "PASSWORD" in env_var:
                        secret_type = "password"
                    elif "API_KEY" in env_var:
                        secret_type = "api_key"
                    elif "JWT" in env_var:
                        secret_type = "jwt_token"
                    elif "ENCRYPTION" in env_var:
                        secret_type = "encryption_key"

                    result = self.secrets_api.create_secret(
                        name=f"migrated_env_{env_var.lower()}",
                        value=env_value,
                        secret_type=secret_type,
                        description=f"Мигрированная переменная окружения {env_var}",
                        tags={
                            "migrated": "true",
                            "source": "environment",
                            "env_var": env_var,
                        },
                    )

                    if result.get("success"):
                        self.log_activity(
                            f"Мигрирована переменная окружения: {env_var}"
                        )

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции из переменных окружения: {e}", "error"
            )

    def _migrate_from_database(self) -> None:
        """Миграция секретов из базы данных"""
        try:
            # Поиск файлов базы данных
            db_files = ["data/users.db", "data/secrets.db", "data/config.db"]

            for db_file in db_files:
                db_path = Path(db_file)
                if db_path.exists():
                    self._migrate_database_file(db_path)

        except Exception as e:
            self.log_activity(f"Ошибка миграции из базы данных: {e}", "error")

    def _migrate_database_file(self, db_path: Path) -> None:
        """Миграция секретов из файла базы данных"""
        try:
            import sqlite3

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Поиск таблиц с секретами
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            tables = cursor.fetchall()

            for (table_name,) in tables:
                if any(
                    keyword in table_name.lower()
                    for keyword in ["password", "secret", "key", "token"]
                ):
                    self._migrate_table(cursor, table_name)

            conn.close()
            self.log_activity(f"Миграция из БД {db_path} завершена")

        except Exception as e:
            self.log_activity(f"Ошибка миграции из БД {db_path}: {e}", "error")

    def _migrate_table(self, cursor, table_name: str) -> None:
        """Миграция секретов из таблицы"""
        try:
            # Получение структуры таблицы
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            # Поиск колонок с секретами
            secret_columns = []
            for column in columns:
                column_name = column[1]
                if any(
                    keyword in column_name.lower()
                    for keyword in ["password", "secret", "key", "token"]
                ):
                    secret_columns.append(column_name)

            if secret_columns:
                # Получение данных
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()

                for row in rows:
                    for i, column in enumerate(columns):
                        if column[1] in secret_columns:
                            secret_value = row[i]
                            if secret_value:
                                result = self.secrets_api.create_secret(
                                    name=f"migrated_db_{table_name}_{column[1]}_{row[0]}",
                                    value=str(secret_value),
                                    secret_type="custom",
                                    description=f"Мигрированный секрет из БД {table_name}.{column[1]}",
                                    tags={
                                        "migrated": "true",
                                        "source": "database",
                                        "table": table_name,
                                        "column": column[1],
                                    },
                                )

                                if result.get("success"):
                                    self.log_activity(
                                        f"Мигрирован секрет из БД: {table_name}.{column[1]}"
                                    )

        except Exception as e:
            self.log_activity(
                f"Ошибка миграции таблицы {table_name}: {e}", "error"
            )

    def get_integration_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        try:
            # Получение статистики секретов
            stats = self.secrets_api.get_statistics()

            # Подсчет мигрированных секретов
            migrated_count = 0
            if stats.get("success"):
                secrets_list = self.secrets_api.list_secrets()
                if secrets_list.get("success"):
                    for secret in secrets_list["secrets"]:
                        metadata = self.secrets_api.get_secret_metadata(
                            secret["secret_id"]
                        )
                        if metadata.get("success"):
                            tags = metadata["metadata"].get("tags", {})
                            if tags.get("migrated") == "true":
                                migrated_count += 1

            return {
                "success": True,
                "integration_status": {
                    "status": self.status.value,
                    "migrated_secrets_count": migrated_count,
                    "total_secrets_count": stats.get("statistics", {}).get(
                        "total_secrets", 0
                    ),
                    "components_integrated": len(
                        self.integration_config.get("components", {})
                    ),
                    "adapters_created": (
                        len(list(Path("security/adapters").glob("*.py")))
                        if Path("security/adapters").exists()
                        else 0
                    ),
                },
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса интеграции: {e}", "error"
            )
            return {"error": str(e)}

    def stop(self) -> bool:
        """Остановка интеграции"""
        try:
            self.log_activity("Остановка интеграции секретов...")

            # Сохранение конфигурации
            self._save_integration_config()

            self.status = ComponentStatus.STOPPED
            self.log_activity("Интеграция секретов остановлена")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка остановки интеграции: {e}", "error")
            return False


# Глобальный экземпляр интеграции
_secrets_integration_instance = None


def get_secrets_integration() -> SecretsIntegration:
    """Получение глобального экземпляра интеграции секретов"""
    global _secrets_integration_instance
    if _secrets_integration_instance is None:
        _secrets_integration_instance = SecretsIntegration()
        _secrets_integration_instance.initialize()
    return _secrets_integration_instance


def initialize_secrets_integration() -> SecretsIntegration:
    """Инициализация глобальной интеграции секретов"""
    global _secrets_integration_instance
    _secrets_integration_instance = SecretsIntegration()
    _secrets_integration_instance.initialize()
    return _secrets_integration_instance


if __name__ == "__main__":
    # Пример использования интеграции
    integration = initialize_secrets_integration()

    # Получение статуса интеграции
    status = integration.get_integration_status()
    print(f"Статус интеграции: {status}")

    # Остановка интеграции
    integration.stop()
