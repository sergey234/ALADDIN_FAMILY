# Active Network Monitoring - Документация файла v2.5

## Общая информация
- **Файл**: `security/active/network_monitoring.py`
- **Размер**: 639 строк (29,264 байт)
- **Версия**: 1.0
- **Дата создания**: 2025-09-02
- **Статус**: КРИТИЧНО (Семейная безопасность)

## Структура файла

### Импорты
```python
import logging
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from core.base import SecurityBase
```

### Классы

#### 1. NetworkType (Enum)
- WIFI = "wifi"
- ETHERNET = "ethernet"
- MOBILE = "mobile"
- BLUETOOTH = "bluetooth"
- VPN = "vpn"
- UNKNOWN = "unknown"

#### 2. TrafficType (Enum)
- WEB = "web"
- EMAIL = "email"
- GAMING = "gaming"
- SOCIAL_MEDIA = "social_media"
- STREAMING = "streaming"
- DOWNLOAD = "download"
- UPLOAD = "upload"
- CHAT = "chat"
- FILE_SHARING = "file_sharing"
- UNKNOWN = "unknown"

#### 3. ThreatLevel (Enum)
- LOW = "low"
- MEDIUM = "medium"
- HIGH = "high"
- CRITICAL = "critical"

#### 4. MonitoringAction (Enum)
- LOG = "log"
- ALERT = "alert"
- BLOCK = "block"
- THROTTLE = "throttle"
- QUARANTINE = "quarantine"
- NOTIFY_PARENT = "notify_parent"
- NOTIFY_ADMIN = "notify_admin"
- SCAN_DEEP = "scan_deep"

#### 5. NetworkConnection (dataclass)
**Поля:**
- `connection_id: str`
- `source_ip: str`
- `destination_ip: str`
- `source_port: int`
- `destination_port: int`
- `protocol: str`
- `network_type: NetworkType`
- `traffic_type: TrafficType`
- `bytes_sent: int`
- `bytes_received: int`
- `start_time: datetime`
- `end_time: Optional[datetime]`
- `duration: Optional[float]`
- `user_id: Optional[str]`
- `device_id: Optional[str]`
- `metadata: Dict[str, Any]`

#### 6. NetworkAnomaly (dataclass)
**Поля:**
- `anomaly_id: str`
- `connection_id: str`
- `anomaly_type: str`
- `threat_level: ThreatLevel`
- `description: str`
- `timestamp: datetime`
- `source_ip: str`
- `destination_ip: str`
- `confidence: float`
- `actions_taken: List[MonitoringAction]`
- `metadata: Dict[str, Any]`

#### 7. NetworkRule (dataclass)
**Поля:**
- `rule_id: str`
- `name: str`
- `description: str`
- `conditions: Dict[str, Any]`
- `actions: List[MonitoringAction]`
- `enabled: bool`
- `family_specific: bool`
- `age_group: Optional[str]`
- `time_restrictions: Optional[Dict[str, Any]]`

#### 8. NetworkStatistics (dataclass)
**Поля:**
- `total_connections: int`
- `total_bytes_sent: int`
- `total_bytes_received: int`
- `active_connections: int`
- `blocked_connections: int`
- `anomalies_detected: int`
- `by_traffic_type: Dict[str, int]`
- `by_network_type: Dict[str, int]`
- `by_threat_level: Dict[str, int]`
- `top_destinations: List[Tuple[str, int]]`
- `top_sources: List[Tuple[str, int]]`

#### 9. NetworkMonitoringService (основной класс)
**Наследование:** `SecurityBase`

**Поля:**
- `active_connections: Dict[str, NetworkConnection]`
- `connection_history: List[NetworkConnection]`
- `network_anomalies: Dict[str, NetworkAnomaly]`
- `monitoring_rules: Dict[str, NetworkRule]`
- `blocked_ips: Set[str]`
- `throttled_ips: Set[str]`
- `family_network_history: Dict[str, List[str]]`
- `monitoring_enabled: bool`
- `real_time_monitoring: bool`
- `deep_packet_inspection: bool`
- `family_protection_enabled: bool`
- `child_monitoring_mode: bool`
- `elderly_monitoring_mode: bool`
- `anomaly_thresholds: Dict[ThreatLevel, float]`

**Методы (20+):**
- `__init__(name: str, config: Optional[Dict[str, Any]])`
- `_initialize_monitoring_rules()`
- `_setup_family_protection()`
- `_start_monitoring()`
- `monitor_connection(...) -> NetworkConnection`
- `_detect_network_type(destination_ip: str) -> NetworkType`
- `_detect_traffic_type(port: int, protocol: str) -> TrafficType`
- `_check_monitoring_rules(connection: NetworkConnection)`
- `_evaluate_rule_conditions(connection: NetworkConnection, rule: NetworkRule) -> bool`
- `_apply_rule_actions(connection: NetworkConnection, rule: NetworkRule)`
- `_is_malicious_ip(ip: str) -> bool`
- `_is_inappropriate_content(ip: str) -> bool`
- `_is_financial_site(ip: str) -> bool`
- `_detect_data_exfiltration(connection: NetworkConnection) -> bool`
- `detect_network_anomaly(...) -> NetworkAnomaly`
- `_determine_threat_level(confidence: float) -> ThreatLevel`
- `get_network_statistics(user_id: Optional[str]) -> NetworkStatistics`
- `get_family_network_status() -> Dict[str, Any]`
- `get_status() -> Dict[str, Any]`
- `_generate_connection_id() -> str`
- `_generate_anomaly_id() -> str`

## Анализ качества кода

### Положительные стороны
1. ✅ Отличная типизация с использованием `typing`
2. ✅ Использование `dataclass` для структурированных данных
3. ✅ Использование `Enum` для констант
4. ✅ Наследование от `SecurityBase` (интеграция с системой)
5. ✅ Подробная документация методов
6. ✅ Обработка ошибок с логированием
7. ✅ Семейная защита (детский/пожилой режимы)
8. ✅ Модульная архитектура
9. ✅ Реальное время мониторинга
10. ✅ Глубокий анализ пакетов

### Проблемы для исправления
1. ⚠️ Длинные строки (E501) - 37 ошибок
2. ⚠️ Нужна проверка на соответствие PEP8

## Зависимости
- `logging` - стандартная библиотека ✅
- `time` - стандартная библиотека ✅
- `typing` - стандартная библиотека ✅
- `datetime` - стандартная библиотека ✅
- `dataclasses` - стандартная библиотека ✅
- `enum` - стандартная библиотека ✅
- `core.base` - внутренний модуль ✅

## Связанные файлы
- `core/base.py` - базовый класс SecurityBase
- `tests/test_network_monitoring.py` - тесты
- `data/sfm/function_registry.json` - регистр функций

## Семейные функции
- **Детская защита**: Мониторинг игр, социальных сетей, блокировка неподходящего контента
- **Защита пожилых**: Мониторинг финансовых сайтов, защита от фишинга
- **Общая семейная защита**: Единая политика, уведомления, блокировка

## Оценка сложности
- **Строк кода**: 639 (в 1.9 раза больше базовой версии)
- **Классов**: 9
- **Методов**: 20+
- **Ошибок flake8**: 37 (только E501)
- **Время на исправление**: ~45-60 минут
- **Приоритет**: ВЫСОКИЙ (критичный семейный модуль)

## Рекомендации
1. Запустить `flake8` для выявления проблем
2. Применить `black` для форматирования
3. Проверить соответствие PEP8
4. Убедиться в работоспособности после изменений
5. Интегрировать в SFM систему
6. Протестировать семейные функции

## Преимущества над базовой версией
- **В 1.9 раза больше** функционала
- **Семейная защита** (детский/пожилой режимы)
- **Интеграция с SecurityBase**
- **Реальное время мониторинга**
- **Глубокий анализ пакетов**
- **Расширенные правила мониторинга**
- **Статистика и аналитика**