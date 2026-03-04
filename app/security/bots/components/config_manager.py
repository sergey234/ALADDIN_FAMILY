"""
Менеджер конфигурации для ParentalControlBot.

Обеспечивает централизованное управление настройками,
валидацию конфигурации и поддержку различных форматов.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigFormat(Enum):
    """Поддерживаемые форматы конфигурации."""

    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""

    url: str = "sqlite:///parental_control.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Конфигурация Redis."""

    url: str = "redis://localhost:6379/0"
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class SecurityConfig:
    """Конфигурация безопасности."""

    encryption_master_password: str = ""
    encryption_key_rotation_days: int = 30
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    password_min_length: int = 8
    require_special_chars: bool = True


@dataclass
class MonitoringConfig:
    """Конфигурация мониторинга."""

    content_analysis_enabled: bool = True
    location_tracking_enabled: bool = True
    social_media_monitoring: bool = True
    real_time_monitoring: bool = True
    ml_enabled: bool = True
    adaptive_learning: bool = True
    metrics_enabled: bool = True
    logging_enabled: bool = True


@dataclass
class NotificationConfig:
    """Конфигурация уведомлений."""

    email_enabled: bool = False
    sms_enabled: bool = False
    push_enabled: bool = True
    emergency_alerts: bool = True
    bedtime_mode: bool = True
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    twilio_sid: str = ""
    twilio_token: str = ""


@dataclass
class CacheConfig:
    """Конфигурация кэширования."""

    max_size: int = 1000
    max_memory_mb: int = 100
    default_ttl: int = 3600
    strategy: str = "lru"
    cleanup_interval: int = 300


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""

    level: str = "INFO"
    log_file: str = "logs/parental_control.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_metrics: bool = True
    format: str = "json"


@dataclass
class ParentalControlConfig:
    """Основная конфигурация ParentalControlBot."""

    # Основные настройки
    bot_name: str = "ParentalControlBot"
    version: str = "2.5"
    debug: bool = False

    # Компоненты конфигурации
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    notification: NotificationConfig = field(
        default_factory=NotificationConfig
    )
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Дополнительные настройки
    cleanup_interval: int = 300
    educational_recommendations: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать конфигурацию в словарь."""
        return {
            "bot_name": self.bot_name,
            "version": self.version,
            "debug": self.debug,
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout,
                "pool_recycle": self.database.pool_recycle,
                "echo": self.database.echo,
            },
            "redis": {
                "url": self.redis.url,
                "max_connections": self.redis.max_connections,
                "socket_timeout": self.redis.socket_timeout,
                "socket_connect_timeout": self.redis.socket_connect_timeout,
                "retry_on_timeout": self.redis.retry_on_timeout,
                "health_check_interval": self.redis.health_check_interval,
            },
            "security": {
                "encryption_master_password": (
                    self.security.encryption_master_password
                ),
                "encryption_key_rotation_days": (
                    self.security.encryption_key_rotation_days
                ),
                "session_timeout": self.security.session_timeout,
                "max_login_attempts": self.security.max_login_attempts,
                "lockout_duration": self.security.lockout_duration,
                "password_min_length": (
                    self.security.password_min_length
                ),
                "require_special_chars": (
                    self.security.require_special_chars
                ),
            },
            "monitoring": {
                "content_analysis_enabled": (
                    self.monitoring.content_analysis_enabled
                ),
                "location_tracking_enabled": (
                    self.monitoring.location_tracking_enabled
                ),
                "social_media_monitoring": (
                    self.monitoring.social_media_monitoring
                ),
                "real_time_monitoring": self.monitoring.real_time_monitoring,
                "ml_enabled": self.monitoring.ml_enabled,
                "adaptive_learning": self.monitoring.adaptive_learning,
                "metrics_enabled": self.monitoring.metrics_enabled,
                "logging_enabled": self.monitoring.logging_enabled,
            },
            "notification": {
                "email_enabled": self.notification.email_enabled,
                "sms_enabled": self.notification.sms_enabled,
                "push_enabled": self.notification.push_enabled,
                "emergency_alerts": self.notification.emergency_alerts,
                "bedtime_mode": self.notification.bedtime_mode,
                "smtp_server": self.notification.smtp_server,
                "smtp_port": self.notification.smtp_port,
                "smtp_username": self.notification.smtp_username,
                "smtp_password": self.notification.smtp_password,
                "twilio_sid": self.notification.twilio_sid,
                "twilio_token": self.notification.twilio_token,
            },
            "cache": {
                "max_size": self.cache.max_size,
                "max_memory_mb": self.cache.max_memory_mb,
                "default_ttl": self.cache.default_ttl,
                "strategy": self.cache.strategy,
                "cleanup_interval": self.cache.cleanup_interval,
            },
            "logging": {
                "level": self.logging.level,
                "log_file": self.logging.log_file,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
                "enable_console": self.logging.enable_console,
                "enable_file": self.logging.enable_file,
                "enable_metrics": self.logging.enable_metrics,
                "format": self.logging.format,
            },
            "cleanup_interval": self.cleanup_interval,
            "educational_recommendations": self.educational_recommendations,
        }


class ConfigManager:
    """Менеджер конфигурации для ParentalControlBot."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация менеджера конфигурации.

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path
        self.config = ParentalControlConfig()
        self.logger = logging.getLogger(__name__)

    def load_config(
        self, config_path: Optional[str] = None
    ) -> ParentalControlConfig:
        """
        Загрузить конфигурацию из файла.

        Args:
            config_path: Путь к файлу конфигурации

        Returns:
            Загруженная конфигурация
        """
        if config_path:
            self.config_path = config_path

        if not self.config_path:
            self.logger.warning(
                "Путь к конфигурации не указан, "
                "используется конфигурация по умолчанию"
            )
            return self.config

        if not os.path.exists(self.config_path):
            self.logger.warning(
                f"Файл конфигурации {self.config_path} не найден, "
                f"используется конфигурация по умолчанию"
            )
            return self.config

        try:
            config_data = self._load_config_file(self.config_path)
            self.config = self._parse_config(config_data)
            self.logger.info(f"Конфигурация загружена из {self.config_path}")
            return self.config

        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self.config

    def save_config(
        self,
        config: ParentalControlConfig,
        output_path: Optional[str] = None,
        format: ConfigFormat = ConfigFormat.YAML,
    ) -> bool:
        """
        Сохранить конфигурацию в файл.

        Args:
            config: Конфигурация для сохранения
            output_path: Путь для сохранения
            format: Формат файла

        Returns:
            True если сохранение успешно
        """
        if not output_path:
            output_path = self.config_path

        if not output_path:
            self.logger.error("Путь для сохранения конфигурации не указан")
            return False

        try:
            config_data = config.to_dict()

            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format == ConfigFormat.JSON:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            elif format == ConfigFormat.YAML:
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        config_data,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
            else:
                self.logger.error(f"Неподдерживаемый формат: {format}")
                return False

            self.logger.info(f"Конфигурация сохранена в {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False

    def load_from_env(self) -> ParentalControlConfig:
        """
        Загрузить конфигурацию из переменных окружения.

        Returns:
            Конфигурация из переменных окружения
        """
        config = ParentalControlConfig()

        # Основные настройки
        config.bot_name = os.getenv("PARENTAL_BOT_NAME", config.bot_name)
        config.version = os.getenv("PARENTAL_BOT_VERSION", config.version)
        config.debug = os.getenv("PARENTAL_DEBUG", "false").lower() == "true"

        # База данных
        config.database.url = os.getenv("DATABASE_URL", config.database.url)
        config.database.pool_size = int(
            os.getenv("DB_POOL_SIZE", config.database.pool_size)
        )
        config.database.max_overflow = int(
            os.getenv("DB_MAX_OVERFLOW", config.database.max_overflow)
        )

        # Redis
        config.redis.url = os.getenv("REDIS_URL", config.redis.url)
        config.redis.max_connections = int(
            os.getenv("REDIS_MAX_CONNECTIONS", config.redis.max_connections)
        )

        # Безопасность
        config.security.encryption_master_password = os.getenv(
            "ENCRYPTION_MASTER_PASSWORD",
            config.security.encryption_master_password,
        )
        config.security.encryption_key_rotation_days = int(
            os.getenv(
                "ENCRYPTION_KEY_ROTATION_DAYS",
                config.security.encryption_key_rotation_days,
            )
        )

        # Мониторинг
        config.monitoring.content_analysis_enabled = (
            os.getenv("CONTENT_ANALYSIS_ENABLED", "true").lower() == "true"
        )
        config.monitoring.location_tracking_enabled = (
            os.getenv("LOCATION_TRACKING_ENABLED", "true").lower() == "true"
        )
        config.monitoring.ml_enabled = (
            os.getenv("ML_ENABLED", "true").lower() == "true"
        )

        # Уведомления
        config.notification.email_enabled = (
            os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        )
        config.notification.sms_enabled = (
            os.getenv("SMS_ENABLED", "false").lower() == "true"
        )
        config.notification.smtp_server = os.getenv(
            "SMTP_SERVER", config.notification.smtp_server
        )
        config.notification.smtp_username = os.getenv(
            "SMTP_USERNAME", config.notification.smtp_username
        )
        config.notification.smtp_password = os.getenv(
            "SMTP_PASSWORD", config.notification.smtp_password
        )

        # Логирование
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.log_file = os.getenv(
            "LOG_FILE", config.logging.log_file
        )

        self.config = config
        self.logger.info("Конфигурация загружена из переменных окружения")
        return config

    def validate_config(self, config: ParentalControlConfig) -> List[str]:
        """
        Валидировать конфигурацию.

        Args:
            config: Конфигурация для валидации

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Валидация основных настроек
        if not config.bot_name:
            errors.append("bot_name не может быть пустым")

        if config.version and not config.version.replace(".", "").isdigit():
            errors.append("version должен содержать только цифры и точки")

        # Валидация базы данных
        if not config.database.url:
            errors.append("database.url не может быть пустым")

        if config.database.pool_size <= 0:
            errors.append("database.pool_size должен быть больше 0")

        # Валидация Redis
        if not config.redis.url:
            errors.append("redis.url не может быть пустым")

        # Валидация безопасности
        if (
            config.security.encryption_master_password
            and len(config.security.encryption_master_password) < 8
        ):
            errors.append(
                "encryption_master_password должен содержать "
                "минимум 8 символов"
            )

        if config.security.password_min_length < 6:
            errors.append("password_min_length должен быть минимум 6")

        # Валидация кэша
        if config.cache.max_size <= 0:
            errors.append("cache.max_size должен быть больше 0")

        if config.cache.max_memory_mb <= 0:
            errors.append(
                "cache.max_memory_mb должен быть больше 0"
            )

        # Валидация логирования
        valid_log_levels = [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ]
        if config.logging.level.upper() not in valid_log_levels:
            errors.append(
                f"logging.level должен быть одним из: "
                f"{', '.join(valid_log_levels)}"
            )

        return errors

    def get_config_schema(self) -> Dict[str, Any]:
        """
        Получить схему конфигурации.

        Returns:
            JSON схема конфигурации
        """
        return {
            "type": "object",
            "properties": {
                "bot_name": {"type": "string", "minLength": 1},
                "version": {"type": "string", "pattern": r"^\d+\.\d+$"},
                "debug": {"type": "boolean"},
                "database": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "minLength": 1},
                        "pool_size": {"type": "integer", "minimum": 1},
                        "max_overflow": {"type": "integer", "minimum": 0},
                        "pool_timeout": {"type": "integer", "minimum": 1},
                        "pool_recycle": {"type": "integer", "minimum": 1},
                        "echo": {"type": "boolean"},
                    },
                    "required": ["url"],
                },
                "redis": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "minLength": 1},
                        "max_connections": {"type": "integer", "minimum": 1},
                        "socket_timeout": {"type": "integer", "minimum": 1},
                        "socket_connect_timeout": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "retry_on_timeout": {"type": "boolean"},
                        "health_check_interval": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "required": ["url"],
                },
                "security": {
                    "type": "object",
                    "properties": {
                        "encryption_master_password": {
                            "type": "string",
                            "minLength": 8,
                        },
                        "encryption_key_rotation_days": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "session_timeout": {"type": "integer", "minimum": 60},
                        "max_login_attempts": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "lockout_duration": {"type": "integer", "minimum": 60},
                        "password_min_length": {
                            "type": "integer",
                            "minimum": 6,
                        },
                        "require_special_chars": {"type": "boolean"},
                    },
                },
                "monitoring": {
                    "type": "object",
                    "properties": {
                        "content_analysis_enabled": {"type": "boolean"},
                        "location_tracking_enabled": {"type": "boolean"},
                        "social_media_monitoring": {"type": "boolean"},
                        "real_time_monitoring": {"type": "boolean"},
                        "ml_enabled": {"type": "boolean"},
                        "adaptive_learning": {"type": "boolean"},
                        "metrics_enabled": {"type": "boolean"},
                        "logging_enabled": {"type": "boolean"},
                    },
                },
                "notification": {
                    "type": "object",
                    "properties": {
                        "email_enabled": {"type": "boolean"},
                        "sms_enabled": {"type": "boolean"},
                        "push_enabled": {"type": "boolean"},
                        "emergency_alerts": {"type": "boolean"},
                        "bedtime_mode": {"type": "boolean"},
                        "smtp_server": {"type": "string"},
                        "smtp_port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535,
                        },
                        "smtp_username": {"type": "string"},
                        "smtp_password": {"type": "string"},
                        "twilio_sid": {"type": "string"},
                        "twilio_token": {"type": "string"},
                    },
                },
                "cache": {
                    "type": "object",
                    "properties": {
                        "max_size": {"type": "integer", "minimum": 1},
                        "max_memory_mb": {"type": "integer", "minimum": 1},
                        "default_ttl": {"type": "integer", "minimum": 1},
                        "strategy": {
                            "type": "string",
                            "enum": ["lru", "lfu", "fifo"],
                        },
                        "cleanup_interval": {"type": "integer", "minimum": 1},
                    },
                },
                "logging": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": [
                                "DEBUG",
                                "INFO",
                                "WARNING",
                                "ERROR",
                                "CRITICAL",
                            ],
                        },
                        "log_file": {"type": "string"},
                        "max_file_size": {"type": "integer", "minimum": 1024},
                        "backup_count": {"type": "integer", "minimum": 1},
                        "enable_console": {"type": "boolean"},
                        "enable_file": {"type": "boolean"},
                        "enable_metrics": {"type": "boolean"},
                        "format": {"type": "string", "enum": ["json", "text"]},
                    },
                },
                "cleanup_interval": {"type": "integer", "minimum": 60},
                "educational_recommendations": {"type": "boolean"},
            },
            "required": ["bot_name", "database", "redis"],
        }

    def _load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Загрузить данные конфигурации из файла."""
        file_ext = Path(config_path).suffix.lower()

        with open(config_path, "r", encoding="utf-8") as f:
            if file_ext in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif file_ext == ".json":
                return json.load(f)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_ext}")

    def _parse_config(
        self, config_data: Dict[str, Any]
    ) -> ParentalControlConfig:
        """Парсить данные конфигурации в объект конфигурации."""
        config = ParentalControlConfig()

        # Основные настройки
        config.bot_name = config_data.get("bot_name", config.bot_name)
        config.version = config_data.get("version", config.version)
        config.debug = config_data.get("debug", config.debug)

        # База данных
        if "database" in config_data:
            db_config = config_data["database"]
            config.database.url = db_config.get("url", config.database.url)
            config.database.pool_size = db_config.get(
                "pool_size", config.database.pool_size
            )
            config.database.max_overflow = db_config.get(
                "max_overflow", config.database.max_overflow
            )
            config.database.pool_timeout = db_config.get(
                "pool_timeout", config.database.pool_timeout
            )
            config.database.pool_recycle = db_config.get(
                "pool_recycle", config.database.pool_recycle
            )
            config.database.echo = db_config.get("echo", config.database.echo)

        # Redis
        if "redis" in config_data:
            redis_config = config_data["redis"]
            config.redis.url = redis_config.get("url", config.redis.url)
            config.redis.max_connections = redis_config.get(
                "max_connections", config.redis.max_connections
            )
            config.redis.socket_timeout = redis_config.get(
                "socket_timeout", config.redis.socket_timeout
            )
            config.redis.socket_connect_timeout = redis_config.get(
                "socket_connect_timeout", config.redis.socket_connect_timeout
            )
            config.redis.retry_on_timeout = redis_config.get(
                "retry_on_timeout", config.redis.retry_on_timeout
            )
            config.redis.health_check_interval = redis_config.get(
                "health_check_interval", config.redis.health_check_interval
            )

        # Безопасность
        if "security" in config_data:
            security_config = config_data["security"]
            config.security.encryption_master_password = security_config.get(
                "encryption_master_password",
                config.security.encryption_master_password,
            )
            config.security.encryption_key_rotation_days = security_config.get(
                "encryption_key_rotation_days",
                config.security.encryption_key_rotation_days,
            )
            config.security.session_timeout = security_config.get(
                "session_timeout", config.security.session_timeout
            )
            config.security.max_login_attempts = security_config.get(
                "max_login_attempts", config.security.max_login_attempts
            )
            config.security.lockout_duration = security_config.get(
                "lockout_duration", config.security.lockout_duration
            )
            config.security.password_min_length = security_config.get(
                "password_min_length", config.security.password_min_length
            )
            config.security.require_special_chars = security_config.get(
                "require_special_chars", config.security.require_special_chars
            )

        # Мониторинг
        if "monitoring" in config_data:
            monitoring_config = config_data["monitoring"]
            config.monitoring.content_analysis_enabled = monitoring_config.get(
                "content_analysis_enabled",
                config.monitoring.content_analysis_enabled,
            )
            config.monitoring.location_tracking_enabled = (
                monitoring_config.get(
                    "location_tracking_enabled",
                    config.monitoring.location_tracking_enabled,
                )
            )
            config.monitoring.social_media_monitoring = monitoring_config.get(
                "social_media_monitoring",
                config.monitoring.social_media_monitoring,
            )
            config.monitoring.real_time_monitoring = monitoring_config.get(
                "real_time_monitoring", config.monitoring.real_time_monitoring
            )
            config.monitoring.ml_enabled = monitoring_config.get(
                "ml_enabled", config.monitoring.ml_enabled
            )
            config.monitoring.adaptive_learning = monitoring_config.get(
                "adaptive_learning", config.monitoring.adaptive_learning
            )
            config.monitoring.metrics_enabled = monitoring_config.get(
                "metrics_enabled", config.monitoring.metrics_enabled
            )
            config.monitoring.logging_enabled = monitoring_config.get(
                "logging_enabled", config.monitoring.logging_enabled
            )

        # Уведомления
        if "notification" in config_data:
            notification_config = config_data["notification"]
            config.notification.email_enabled = notification_config.get(
                "email_enabled", config.notification.email_enabled
            )
            config.notification.sms_enabled = notification_config.get(
                "sms_enabled", config.notification.sms_enabled
            )
            config.notification.push_enabled = notification_config.get(
                "push_enabled", config.notification.push_enabled
            )
            config.notification.emergency_alerts = notification_config.get(
                "emergency_alerts", config.notification.emergency_alerts
            )
            config.notification.bedtime_mode = notification_config.get(
                "bedtime_mode", config.notification.bedtime_mode
            )
            config.notification.smtp_server = notification_config.get(
                "smtp_server", config.notification.smtp_server
            )
            config.notification.smtp_port = notification_config.get(
                "smtp_port", config.notification.smtp_port
            )
            config.notification.smtp_username = notification_config.get(
                "smtp_username", config.notification.smtp_username
            )
            config.notification.smtp_password = notification_config.get(
                "smtp_password", config.notification.smtp_password
            )
            config.notification.twilio_sid = notification_config.get(
                "twilio_sid", config.notification.twilio_sid
            )
            config.notification.twilio_token = notification_config.get(
                "twilio_token", config.notification.twilio_token
            )

        # Кэш
        if "cache" in config_data:
            cache_config = config_data["cache"]
            config.cache.max_size = cache_config.get(
                "max_size", config.cache.max_size
            )
            config.cache.max_memory_mb = cache_config.get(
                "max_memory_mb", config.cache.max_memory_mb
            )
            config.cache.default_ttl = cache_config.get(
                "default_ttl", config.cache.default_ttl
            )
            config.cache.strategy = cache_config.get(
                "strategy", config.cache.strategy
            )
            config.cache.cleanup_interval = cache_config.get(
                "cleanup_interval", config.cache.cleanup_interval
            )

        # Логирование
        if "logging" in config_data:
            logging_config = config_data["logging"]
            config.logging.level = logging_config.get(
                "level", config.logging.level
            )
            config.logging.log_file = logging_config.get(
                "log_file", config.logging.log_file
            )
            config.logging.max_file_size = logging_config.get(
                "max_file_size", config.logging.max_file_size
            )
            config.logging.backup_count = logging_config.get(
                "backup_count", config.logging.backup_count
            )
            config.logging.enable_console = logging_config.get(
                "enable_console", config.logging.enable_console
            )
            config.logging.enable_file = logging_config.get(
                "enable_file", config.logging.enable_file
            )
            config.logging.enable_metrics = logging_config.get(
                "enable_metrics", config.logging.enable_metrics
            )
            config.logging.format = logging_config.get(
                "format", config.logging.format
            )

        # Дополнительные настройки
        config.cleanup_interval = config_data.get(
            "cleanup_interval", config.cleanup_interval
        )
        config.educational_recommendations = config_data.get(
            "educational_recommendations", config.educational_recommendations
        )

        return config
