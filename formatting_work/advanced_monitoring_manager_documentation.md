# Документация: advanced_monitoring_manager.py

## Общая информация
- **Файл**: `security/advanced_monitoring_manager.py`
- **Размер**: 568 строк
- **Назначение**: Расширенный мониторинг системы с метриками, алертами и дашбордом
- **Дата анализа**: 2025-01-27

## Структура файла

### Импорты (строки 1-15)
- `asyncio`, `json`, `time`, `threading` - базовые модули
- `psutil` - системные метрики
- `requests` - HTTP запросы
- `datetime`, `timedelta` - работа с временем
- `typing` - типизация
- `dataclasses` - структуры данных
- `enum` - перечисления
- `collections` - коллекции данных
- Локальные импорты из `core.*`

### Классы и перечисления

#### MetricType (строки 17-25)
Перечисление типов метрик:
- SYSTEM, SECURITY, PERFORMANCE, NETWORK, API, DATABASE, CUSTOM

#### AlertSeverity (строки 28-33)
Уровни серьезности алертов:
- INFO, WARNING, ERROR, CRITICAL

#### Metric (строки 36-44)
Структура метрики:
- name, value, metric_type, timestamp, tags, unit

#### Alert (строки 47-58)
Структура алерта:
- alert_id, title, message, severity, metric_name, threshold_value, current_value, timestamp, resolved, tags

#### MonitoringRule (строки 61-71)
Правило мониторинга:
- rule_id, name, metric_name, condition, threshold, severity, enabled, cooldown, last_triggered

### Основной класс

#### AdvancedMonitoringManager (строки 74-568)
Основной класс менеджера мониторинга:

**Инициализация (строки 76-110)**
- Настройка базовых параметров
- Инициализация хранилищ данных
- Запуск мониторинга

**Методы сбора метрик:**
- `_collect_system_metrics()` - системные метрики (CPU, память, диск, сеть)
- `_collect_security_metrics()` - метрики безопасности
- `_collect_performance_metrics()` - метрики производительности
- `_collect_api_metrics()` - метрики API

**Методы управления:**
- `add_monitoring_rule()` - добавление правил
- `remove_monitoring_rule()` - удаление правил
- `add_alert_callback()` - добавление callbacks
- `get_metrics()` - получение метрик
- `get_alerts()` - получение алертов
- `get_dashboard_data()` - данные для дашборда
- `get_status()` - статус менеджера
- `stop()` - остановка мониторинга

## Анализ качества кода

### Положительные стороны
1. **Хорошая структура** - четкое разделение на классы и методы
2. **Типизация** - использование typing для всех параметров
3. **Документация** - docstrings для всех методов
4. **Обработка ошибок** - try/except блоки в критических местах
5. **Асинхронность** - использование threading для фоновых задач
6. **Конфигурируемость** - настраиваемые интервалы и правила

### Потенциальные проблемы
1. **Длинные строки** - возможны E501 ошибки
2. **Сложность методов** - некоторые методы довольно длинные
3. **Мок-данные** - использование заглушек вместо реальных данных
4. **Отсутствие тестов** - нет unit тестов
5. **Глобальная переменная** - `advanced_monitoring_manager` в конце файла

## Зависимости
- `psutil` - системные метрики
- `requests` - HTTP запросы
- Локальные модули: `core.base`, `core.security_base`, `core.logging_module`

## Связанные файлы
- `core/base.py` - базовые классы
- `core/security_base.py` - базовая безопасность
- `core/logging_module.py` - логирование
- `data/sfm/function_registry.json` - регистр функций SFM