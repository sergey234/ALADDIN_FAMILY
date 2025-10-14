# Иерархия Классов в policy_engine.py

## 1. Enum Классы (Перечисления)

### 1.1 PolicyType (Enum)
- **Базовый класс:** `enum.Enum`
- **Описание:** Типы политик безопасности
- **Значения:** ACCESS_CONTROL, DATA_PROTECTION, NETWORK_SECURITY, DEVICE_MANAGEMENT, USER_BEHAVIOR, CONTENT_FILTERING, TIME_RESTRICTIONS, LOCATION_BASED, EMERGENCY, COMPLIANCE

### 1.2 PolicyStatus (Enum)
- **Базовый класс:** `enum.Enum`
- **Описание:** Статусы политик
- **Значения:** ACTIVE, INACTIVE, DRAFT, TESTING, DEPRECATED, ERROR

### 1.3 PolicyPriority (Enum)
- **Базовый класс:** `enum.Enum`
- **Описание:** Приоритеты политик
- **Значения:** CRITICAL, HIGH, MEDIUM, LOW

### 1.4 ActionType (Enum)
- **Базовый класс:** `enum.Enum`
- **Описание:** Типы действий политик
- **Значения:** ALLOW, DENY, LOG, NOTIFY, BLOCK, REDIRECT, QUARANTINE

### 1.5 ConditionOperator (Enum)
- **Базовый класс:** `enum.Enum`
- **Описание:** Операторы условий
- **Значения:** EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, CONTAINS, NOT_CONTAINS, IN, NOT_IN, REGEX_MATCH, REGEX_NOT_MATCH

## 2. Dataclass Классы (Классы данных)

### 2.1 PolicyCondition (dataclass)
- **Базовый класс:** Нет явного наследования (использует `@dataclass`)
- **Описание:** Условие политики
- **Поля:**
  - `field: str` - Поле для проверки
  - `operator: ConditionOperator` - Оператор сравнения
  - `value: Any` - Значение для сравнения

### 2.2 PolicyAction (dataclass)
- **Базовый класс:** Нет явного наследования (использует `@dataclass`)
- **Описание:** Действие политики
- **Поля:**
  - `action_type: ActionType` - Тип действия
  - `parameters: Dict[str, Any]` - Параметры действия

### 2.3 SecurityPolicy (dataclass)
- **Базовый класс:** Нет явного наследования (использует `@dataclass`)
- **Описание:** Основная политика безопасности
- **Поля:**
  - `policy_id: str` - Идентификатор политики
  - `name: str` - Название политики
  - `description: str` - Описание политики
  - `policy_type: PolicyType` - Тип политики
  - `status: PolicyStatus` - Статус политики
  - `priority: PolicyPriority` - Приоритет политики
  - `conditions: List[PolicyCondition]` - Условия политики
  - `actions: List[PolicyAction]` - Действия политики
  - `target_users: List[str]` - Целевые пользователи
  - `target_devices: List[str]` - Целевые устройства
  - `target_applications: List[str]` - Целевые приложения
  - `created_at: datetime` - Время создания
  - `updated_at: datetime` - Время обновления
  - `version: int` - Версия политики

### 2.4 PolicyEvaluation (dataclass)
- **Базовый класс:** Нет явного наследования (использует `@dataclass`)
- **Описание:** Результат оценки политики
- **Поля:**
  - `policy_id: str` - Идентификатор политики
  - `matched: bool` - Соответствует ли условиям
  - `evaluation_time: float` - Время оценки
  - `timestamp: datetime` - Время оценки
  - `reason: str` - Причина результата

## 3. Основной Класс

### 3.1 PolicyEngine (SecurityBase)
- **Базовый класс:** `core.base.SecurityBase`
- **Описание:** Движок политик безопасности
- **Наследование:** Наследует методы и атрибуты от `SecurityBase` для базовой функциональности безопасности
- **Основные атрибуты:**
  - `policies: Dict[str, SecurityPolicy]` - Словарь политик
  - `policy_evaluations: List[PolicyEvaluation]` - История оценок
  - `policy_cache: Dict[str, List[SecurityPolicy]]` - Кэш политик
  - `evaluation_stats: Dict[str, Any]` - Статистика оценок
  - `enable_caching: bool` - Включен ли кэш
  - `cache_ttl: int` - Время жизни кэша
  - `evaluation_timeout: float` - Таймаут оценки
  - `max_evaluations_per_request: int` - Максимум оценок на запрос

## 4. Иерархия Наследования

```
SecurityBase (core.base.SecurityBase)
    └── PolicyEngine

Enum (enum.Enum)
    ├── PolicyType
    ├── PolicyStatus
    ├── PolicyPriority
    ├── ActionType
    └── ConditionOperator

object (базовый класс)
    ├── PolicyCondition (@dataclass)
    ├── PolicyAction (@dataclass)
    ├── SecurityPolicy (@dataclass)
    └── PolicyEvaluation (@dataclass)
```

## 5. Взаимосвязи Классов

- **PolicyEngine** использует все остальные классы
- **SecurityPolicy** содержит списки **PolicyCondition** и **PolicyAction**
- **PolicyEvaluation** ссылается на **SecurityPolicy** через `policy_id`
- Все Enum классы используются как типы в dataclass классах
- **PolicyEngine** наследует функциональность безопасности от **SecurityBase**

## 6. Полиморфизм

- **PolicyEngine** может использоваться везде, где ожидается **SecurityBase**
- Все Enum классы поддерживают полиморфное поведение через наследование от **Enum**
- **@dataclass** декораторы обеспечивают автоматическую реализацию специальных методов