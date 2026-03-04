#!/usr/bin/env python3
"""
ALADDIN VPN - Protocol Interfaces
Интерфейсы для всех компонентов VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# БАЗОВЫЕ ИНТЕРФЕЙСЫ
# ============================================================================


class VPNComponent(ABC):
    """Базовый интерфейс для всех VPN компонентов"""

    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация компонента"""
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Корректное завершение работы компонента"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса компонента"""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик компонента"""
        pass


class Configurable(ABC):
    """Интерфейс для конфигурируемых компонентов"""

    @abstractmethod
    def load_config(self, config_path: str) -> bool:
        """Загрузка конфигурации из файла"""
        pass

    @abstractmethod
    def save_config(self, config_path: str) -> bool:
        """Сохранение конфигурации в файл"""
        pass

    @abstractmethod
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Валидация конфигурации"""
        pass


class Monitorable(ABC):
    """Интерфейс для мониторируемых компонентов"""

    @abstractmethod
    def start_monitoring(self) -> bool:
        """Запуск мониторинга"""
        pass

    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Остановка мониторинга"""
        pass

    @abstractmethod
    def get_health_status(self) -> str:
        """Получение статуса здоровья"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ VPN СЕРВЕРОВ
# ============================================================================


class VPNServer(VPNComponent, Configurable, Monitorable):
    """Интерфейс VPN сервера"""

    @abstractmethod
    def start_server(self) -> bool:
        """Запуск VPN сервера"""
        pass

    @abstractmethod
    def stop_server(self) -> bool:
        """Остановка VPN сервера"""
        pass

    @abstractmethod
    def add_client(self, client_config: Dict[str, Any]) -> bool:
        """Добавление клиента"""
        pass

    @abstractmethod
    def remove_client(self, client_id: str) -> bool:
        """Удаление клиента"""
        pass

    @abstractmethod
    def get_connected_clients(self) -> List[Dict[str, Any]]:
        """Получение списка подключенных клиентов"""
        pass

    @abstractmethod
    def get_server_info(self) -> Dict[str, Any]:
        """Получение информации о сервере"""
        pass


class VPNClient(VPNComponent, Configurable):
    """Интерфейс VPN клиента"""

    @abstractmethod
    def connect(self, server_config: Dict[str, Any]) -> bool:
        """Подключение к VPN серверу"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Отключение от VPN сервера"""
        pass

    @abstractmethod
    def reconnect(self) -> bool:
        """Переподключение"""
        pass

    @abstractmethod
    def get_connection_status(self) -> str:
        """Получение статуса подключения"""
        pass

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Получение информации о подключении"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ БЕЗОПАСНОСТИ
# ============================================================================


class SecurityManager(VPNComponent, Configurable, Monitorable):
    """Интерфейс менеджера безопасности"""

    @abstractmethod
    def check_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Проверка запроса на безопасность"""
        pass

    @abstractmethod
    def block_ip(self, ip_address: str, reason: str) -> bool:
        """Блокировка IP адреса"""
        pass

    @abstractmethod
    def unblock_ip(self, ip_address: str) -> bool:
        """Разблокировка IP адреса"""
        pass

    @abstractmethod
    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение событий безопасности"""
        pass


class DDoSProtection(SecurityManager):
    """Интерфейс защиты от DDoS"""

    @abstractmethod
    def analyze_traffic(self, traffic_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Анализ трафика на предмет DDoS атак"""
        pass

    @abstractmethod
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Получение статистики атак"""
        pass


class RateLimiter(SecurityManager):
    """Интерфейс ограничения скорости"""

    @abstractmethod
    def check_rate_limit(self, identifier: str, endpoint: str, tokens: int = 1) -> Tuple[bool, str, str]:
        """Проверка ограничения скорости"""
        pass

    @abstractmethod
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """Добавление правила ограничения"""
        pass

    @abstractmethod
    def remove_rule(self, rule_id: str) -> bool:
        """Удаление правила ограничения"""
        pass


class IntrusionDetection(SecurityManager):
    """Интерфейс обнаружения вторжений"""

    @abstractmethod
    def analyze_request(self, request_data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Анализ запроса на предмет вторжений"""
        pass

    @abstractmethod
    def add_honeypot(self, honeypot_config: Dict[str, Any]) -> bool:
        """Добавление honeypot эндпоинта"""
        pass

    @abstractmethod
    def get_threat_events(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Получение событий угроз"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ АУТЕНТИФИКАЦИИ
# ============================================================================


class AuthenticationManager(VPNComponent, Configurable):
    """Интерфейс менеджера аутентификации"""

    @abstractmethod
    def authenticate_user(self, credentials: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Аутентификация пользователя"""
        pass

    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Создание пользователя"""
        pass

    @abstractmethod
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Обновление пользователя"""
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Удаление пользователя"""
        pass


class TwoFactorAuth(AuthenticationManager):
    """Интерфейс двухфакторной аутентификации"""

    @abstractmethod
    def setup_2fa(self, user_id: str, methods: List[str]) -> Dict[str, Any]:
        """Настройка 2FA для пользователя"""
        pass

    @abstractmethod
    def verify_2fa_code(self, user_id: str, code: str, method: str) -> Tuple[bool, str]:
        """Проверка 2FA кода"""
        pass

    @abstractmethod
    def send_verification_code(self, user_id: str, method: str) -> Tuple[bool, str]:
        """Отправка кода верификации"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ ЛОГИРОВАНИЯ И АУДИТА
# ============================================================================


class Logger(VPNComponent):
    """Интерфейс логгера"""

    @abstractmethod
    def log_event(self, level: str, message: str, data: Dict[str, Any] = None) -> bool:
        """Логирование события"""
        pass

    @abstractmethod
    def get_logs(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение логов"""
        pass

    @abstractmethod
    def cleanup_logs(self, retention_days: int = 30) -> bool:
        """Очистка старых логов"""
        pass


class AuditLogger(Logger):
    """Интерфейс аудит логгера"""

    @abstractmethod
    def log_security_event(
        self, event_type: str, message: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None
    ) -> str:
        """Логирование события безопасности"""
        pass

    @abstractmethod
    def get_audit_events(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Получение событий аудита"""
        pass

    @abstractmethod
    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Генерация отчета аудита"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ МОНИТОРИНГА
# ============================================================================


class MonitoringManager(VPNComponent, Monitorable):
    """Интерфейс менеджера мониторинга"""

    @abstractmethod
    def start_monitoring(self) -> bool:
        """Запуск мониторинга"""
        pass

    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Остановка мониторинга"""
        pass

    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]:
        """Получение системных метрик"""
        pass

    @abstractmethod
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Получение правил алертов"""
        pass

    @abstractmethod
    def add_alert_rule(self, rule: Dict[str, Any]) -> bool:
        """Добавление правила алерта"""
        pass


class MetricsCollector(VPNComponent):
    """Интерфейс сборщика метрик"""

    @abstractmethod
    def collect_metrics(self) -> Dict[str, Any]:
        """Сбор метрик"""
        pass

    @abstractmethod
    def get_metric_history(self, metric_name: str, time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Получение истории метрики"""
        pass

    @abstractmethod
    def export_metrics(self, format: str = "json") -> str:
        """Экспорт метрик"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ КОНФИГУРАЦИИ
# ============================================================================


class ConfigurationManager(VPNComponent, Configurable):
    """Интерфейс менеджера конфигурации"""

    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        pass

    @abstractmethod
    def reload_config(self) -> bool:
        """Перезагрузка конфигурации"""
        pass

    @abstractmethod
    def backup_config(self, backup_path: str) -> bool:
        """Резервное копирование конфигурации"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ СЕТИ
# ============================================================================


class NetworkManager(VPNComponent, Configurable):
    """Интерфейс менеджера сети"""

    @abstractmethod
    def create_tunnel(self, tunnel_config: Dict[str, Any]) -> bool:
        """Создание туннеля"""
        pass

    @abstractmethod
    def destroy_tunnel(self, tunnel_id: str) -> bool:
        """Уничтожение туннеля"""
        pass

    @abstractmethod
    def get_network_status(self) -> Dict[str, Any]:
        """Получение статуса сети"""
        pass

    @abstractmethod
    def configure_routing(self, routing_config: Dict[str, Any]) -> bool:
        """Настройка маршрутизации"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ ШИФРОВАНИЯ
# ============================================================================


class EncryptionManager(VPNComponent, Configurable):
    """Интерфейс менеджера шифрования"""

    @abstractmethod
    def generate_keys(self, key_type: str, key_size: int) -> Dict[str, str]:
        """Генерация ключей"""
        pass

    @abstractmethod
    def encrypt_data(self, data: bytes, key: str) -> bytes:
        """Шифрование данных"""
        pass

    @abstractmethod
    def decrypt_data(self, encrypted_data: bytes, key: str) -> bytes:
        """Расшифровка данных"""
        pass

    @abstractmethod
    def sign_data(self, data: bytes, private_key: str) -> bytes:
        """Подписание данных"""
        pass

    @abstractmethod
    def verify_signature(self, data: bytes, signature: bytes, public_key: str) -> bool:
        """Проверка подписи"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ БАЗЫ ДАННЫХ
# ============================================================================


class DatabaseManager(VPNComponent, Configurable):
    """Интерфейс менеджера базы данных"""

    @abstractmethod
    def connect(self) -> bool:
        """Подключение к базе данных"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Отключение от базы данных"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Выполнение запроса"""
        pass

    @abstractmethod
    def backup_database(self, backup_path: str) -> bool:
        """Резервное копирование базы данных"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ API
# ============================================================================


class APIManager(VPNComponent, Configurable):
    """Интерфейс менеджера API"""

    @abstractmethod
    def start_api_server(self) -> bool:
        """Запуск API сервера"""
        pass

    @abstractmethod
    def stop_api_server(self) -> bool:
        """Остановка API сервера"""
        pass

    @abstractmethod
    def register_endpoint(self, endpoint: str, handler: callable, methods: List[str] = None) -> bool:
        """Регистрация эндпоинта"""
        pass

    @abstractmethod
    def get_api_documentation(self) -> Dict[str, Any]:
        """Получение документации API"""
        pass


# ============================================================================
# ИНТЕРФЕЙСЫ ИНТЕГРАЦИИ
# ============================================================================


class IntegrationManager(VPNComponent, Configurable):
    """Интерфейс менеджера интеграций"""

    @abstractmethod
    def register_integration(self, name: str, integration: VPNComponent) -> bool:
        """Регистрация интеграции"""
        pass

    @abstractmethod
    def unregister_integration(self, name: str) -> bool:
        """Отмена регистрации интеграции"""
        pass

    @abstractmethod
    def get_integration_status(self, name: str) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        pass

    @abstractmethod
    def get_all_integrations(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех интеграций"""
        pass


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================================================


@dataclass
class VPNRequest:
    """Класс для VPN запросов"""

    request_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    payload: str = ""
    headers: Dict[str, str] = None
    user_id: str = None
    session_id: str = None


@dataclass
class VPNResponse:
    """Класс для VPN ответов"""

    request_id: str
    status_code: int
    message: str
    data: Dict[str, Any] = None
    headers: Dict[str, str] = None
    response_time_ms: float = 0.0


@dataclass
class SecurityEvent:
    """Класс для событий безопасности"""

    event_id: str
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: str
    description: str
    details: Dict[str, Any] = None
    user_id: str = None


# ============================================================================
# ЭКСПОРТ ИНТЕРФЕЙСОВ
# ============================================================================

__all__ = [
    # Базовые интерфейсы
    "VPNComponent",
    "Configurable",
    "Monitorable",
    # VPN интерфейсы
    "VPNServer",
    "VPNClient",
    # Безопасность
    "SecurityManager",
    "DDoSProtection",
    "RateLimiter",
    "IntrusionDetection",
    # Аутентификация
    "AuthenticationManager",
    "TwoFactorAuth",
    # Логирование
    "Logger",
    "AuditLogger",
    # Мониторинг
    "MonitoringManager",
    "MetricsCollector",
    # Конфигурация
    "ConfigurationManager",
    # Сеть
    "NetworkManager",
    # Шифрование
    "EncryptionManager",
    # База данных
    "DatabaseManager",
    # API
    "APIManager",
    # Интеграции
    "IntegrationManager",
    # Вспомогательные классы
    "VPNRequest",
    "VPNResponse",
    "SecurityEvent",
]
