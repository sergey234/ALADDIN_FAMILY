# Иерархия классов: advanced_monitoring_manager.py

## Общая структура

```
object
└── ABC
    └── CoreBase
        └── SecurityBase
            └── AdvancedMonitoringManager (основной класс)

Enum
├── MetricType (типы метрик)
└── AlertSeverity (уровни серьезности)

dataclass
├── Metric (метрика системы)
├── Alert (алерт системы)
└── MonitoringRule (правило мониторинга)
```

## Детальное описание классов

### 1. AdvancedMonitoringManager
- **Базовый класс**: SecurityBase
- **Тип**: Основной функциональный класс
- **Назначение**: Управление мониторингом системы
- **MRO**: AdvancedMonitoringManager → SecurityBase → CoreBase → ABC → object

### 2. MetricType (Enum)
- **Базовый класс**: Enum
- **Тип**: Перечисление
- **Назначение**: Типы метрик (SYSTEM, SECURITY, PERFORMANCE, etc.)

### 3. AlertSeverity (Enum)
- **Базовый класс**: Enum
- **Тип**: Перечисление
- **Назначение**: Уровни серьезности алертов (INFO, WARNING, ERROR, CRITICAL)

### 4. Metric (dataclass)
- **Базовый класс**: dataclass
- **Тип**: Структура данных
- **Назначение**: Представление метрики системы

### 5. Alert (dataclass)
- **Базовый класс**: dataclass
- **Тип**: Структура данных
- **Назначение**: Представление алерта системы

### 6. MonitoringRule (dataclass)
- **Базовый класс**: dataclass
- **Тип**: Структура данных
- **Назначение**: Представление правила мониторинга

## Полиморфизм
- ✅ AdvancedMonitoringManager корректно наследует от SecurityBase
- ✅ Поддерживается полиморфизм через базовый класс SecurityBase
- ✅ MRO позволяет корректное разрешение методов