# Иерархия классов IPv6 DNS Protection System

## Общая структура

```
object
├── Enum
│   ├── ProtectionLevel
│   └── LeakType
├── dataclass
│   ├── ProtectionRule
│   └── LeakDetection
└── SecurityBase
    └── IPv6DNSProtectionSystem
```

## Детальная иерархия

### 1. ProtectionLevel (Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Уровни защиты системы
- **Значения**:
  - `BASIC = "basic"` - Базовая защита
  - `STANDARD = "standard"` - Стандартная защита
  - `HIGH = "high"` - Высокая защита
  - `MAXIMUM = "maximum"` - Максимальная защита

### 2. LeakType (Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Типы утечек для мониторинга
- **Значения**:
  - `IPV6_LEAK = "ipv6_leak"`
  - `DNS_LEAK = "dns_leak"`
  - `WEBRTC_LEAK = "webrtc_leak"`
  - `TEREDO_LEAK = "teredo_leak"`
  - `SIXTOFOUR_LEAK = "6to4_leak"`

### 3. ProtectionRule (dataclass)
- **Базовый класс**: `object` (через dataclass)
- **Назначение**: Правила защиты системы
- **Атрибуты**:
  - `rule_id: str` - Идентификатор правила
  - `rule_type: str` - Тип правила
  - `action: str` - Действие правила
  - `target: str` - Цель правила
  - `enabled: bool = True` - Включено ли правило
  - `priority: int = 0` - Приоритет правила

### 4. LeakDetection (dataclass)
- **Базовый класс**: `object` (через dataclass)
- **Назначение**: Обнаружение утечек
- **Атрибуты**:
  - `leak_type: LeakType` - Тип утечки
  - `detected: bool` - Обнаружена ли утечка
  - `details: str` - Детали утечки
  - `timestamp: float` - Время обнаружения
  - `severity: str = "medium"` - Серьезность утечки

### 5. IPv6DNSProtectionSystem (SecurityBase)
- **Базовый класс**: `SecurityBase`
- **Цепочка наследования**: `IPv6DNSProtectionSystem` → `SecurityBase` → `CoreBase` → `ABC` → `object`
- **Назначение**: Основная система защиты от IPv6 и DNS утечек
- **Ключевые атрибуты**:
  - `protection_level: ProtectionLevel` - Уровень защиты
  - `kill_switch_enabled: bool` - Включен ли Kill Switch
  - `dns_protection_enabled: bool` - Включена ли DNS защита
  - `ipv6_blocking_enabled: bool` - Включена ли блокировка IPv6
  - `secure_dns_servers: List[str]` - Безопасные DNS серверы
  - `protection_rules: List[ProtectionRule]` - Правила защиты
  - `leak_detections: List[LeakDetection]` - Обнаруженные утечки

## Полиморфизм

### Переопределенные методы
- `__init__()` - Инициализация системы защиты
- `get_protection_status()` - Получение статуса защиты (переопределен из SecurityBase)

### Наследованные методы
- Методы из `SecurityBase` для базовой функциональности безопасности
- Методы из `CoreBase` для базовой функциональности компонентов

## Взаимодействие классов

1. **IPv6DNSProtectionSystem** использует **ProtectionLevel** для настройки уровня защиты
2. **IPv6DNSProtectionSystem** использует **LeakType** для классификации утечек
3. **IPv6DNSProtectionSystem** создает и управляет **ProtectionRule** объектами
4. **IPv6DNSProtectionSystem** создает **LeakDetection** объекты при обнаружении утечек

## Статус наследования
- ✅ **Наследование**: Корректно реализовано
- ✅ **Полиморфизм**: Методы переопределены правильно
- ✅ **Инкапсуляция**: Приватные методы обозначены префиксом `_`
- ✅ **Абстракция**: Четкое разделение ответственности между классами