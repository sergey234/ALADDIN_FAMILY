# Network Monitoring - Документация файла v2.5

## Общая информация
- **Файл**: `security/network_monitoring.py`
- **Размер**: 340 строк
- **Версия**: 1.0
- **Дата создания**: 2025-09-12
- **Статус**: КРИТИЧНО

## Структура файла

### Импорты
```python
import time
import datetime
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
```

### Константы
- `NETWORK_MONITORING_CONFIG = "data/network/monitoring_config.json"`

### Классы

#### 1. NetworkStatus (Enum)
- HEALTHY = "healthy"
- DEGRADED = "degraded" 
- CRITICAL = "critical"
- DOWN = "down"

#### 2. AlertLevel (Enum)
- INFO = "info"
- WARNING = "warning"
- ERROR = "error"
- CRITICAL = "critical"

#### 3. NetworkMetric (dataclass)
**Поля:**
- `metric_name: str`
- `value: float`
- `unit: str`
- `timestamp: str` (автоматически)
- `device_id: Optional[str]`
- `interface: Optional[str]`

**Методы:**
- `to_dict() -> Dict[str, Any]`
- `from_dict(data: Dict[str, Any]) -> 'NetworkMetric'`

#### 4. NetworkAlert (dataclass)
**Поля:**
- `alert_id: str`
- `alert_type: str`
- `level: AlertLevel`
- `message: str`
- `device_id: Optional[str]`
- `interface: Optional[str]`
- `timestamp: str` (автоматически)
- `resolved: bool`

**Методы:**
- `to_dict() -> Dict[str, Any]`
- `from_dict(data: Dict[str, Any]) -> 'NetworkAlert'`

#### 5. NetworkDevice (dataclass)
**Поля:**
- `device_id: str`
- `name: str`
- `ip_address: str`
- `device_type: str`
- `status: NetworkStatus` (по умолчанию HEALTHY)
- `last_seen: str` (автоматически)
- `interfaces: List[str]`

**Методы:**
- `to_dict() -> Dict[str, Any]`
- `from_dict(data: Dict[str, Any]) -> 'NetworkDevice'`

#### 6. NetworkMonitoring (основной класс)
**Поля:**
- `config_path: str`
- `devices: Dict[str, NetworkDevice]`
- `metrics: List[NetworkMetric]`
- `alerts: List[NetworkAlert]`
- `monitoring_rules: List[Dict[str, Any]]`
- `metrics_history: Dict[str, deque]`

**Методы:**
- `__init__(config_path: str = NETWORK_MONITORING_CONFIG)`
- `_load_config()`
- `_create_default_config()`
- `register_device(device: NetworkDevice)`
- `add_metric(metric: NetworkMetric)`
- `_check_alerts(metric: NetworkMetric)`
- `get_device_status(device_id: str) -> Optional[NetworkStatus]`
- `update_device_status(device_id: str, status: NetworkStatus)`
- `get_active_alerts() -> List[NetworkAlert]`
- `resolve_alert(alert_id: str) -> bool`
- `get_metrics_summary() -> Dict[str, Any]`
- `get_network_health_score() -> float`
- `add_monitoring_rule(rule_name: str, metric: str, threshold: float, level: str)`
- `_save_config()`
- `get_device_metrics(device_id: str, metric_name: Optional[str] = None) -> List[NetworkMetric]`
- `cleanup_old_metrics(hours: int = 24)`
- `export_metrics(file_path: str)`
- `get_network_topology() -> Dict[str, Any]`

## Анализ качества кода

### Положительные стороны
1. ✅ Хорошая типизация с использованием `typing`
2. ✅ Использование `dataclass` для структурированных данных
3. ✅ Использование `Enum` для констант
4. ✅ Документация методов
5. ✅ Обработка ошибок в `_load_config()`
6. ✅ Логирование действий
7. ✅ Модульная архитектура

### Потенциальные проблемы
1. ⚠️ Длинные строки (E501)
2. ⚠️ Возможные проблемы с отступами
3. ⚠️ Нужна проверка на соответствие PEP8

## Зависимости
- `time` - стандартная библиотека
- `datetime` - стандартная библиотека  
- `json` - стандартная библиотека
- `os` - стандартная библиотека
- `typing` - стандартная библиотека
- `enum` - стандартная библиотека
- `dataclasses` - стандартная библиотека
- `collections` - стандартная библиотека

## Связанные файлы
- `data/network/monitoring_config.json` - конфигурация
- Тесты: `tests/test_network_monitoring.py`
- Интеграция с SFM: `data/sfm/function_registry.json`

## Оценка сложности
- **Строк кода**: 340
- **Классов**: 6
- **Методов**: 20+
- **Время на исправление**: ~30-45 минут
- **Приоритет**: ВЫСОКИЙ (критичный модуль)

## Рекомендации
1. Запустить `flake8` для выявления проблем
2. Применить `black` для форматирования
3. Проверить соответствие PEP8
4. Убедиться в работоспособности после изменений
5. Интегрировать в SFM систему