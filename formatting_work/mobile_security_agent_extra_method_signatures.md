# Сигнатуры методов mobile_security_agent_extra.py

## Класс ThreatData (dataclass)

### Автоматически генерируемые методы:
- `__init__(self, app_id: str, threat_type: str, severity: str, confidence: float, timestamp: datetime, details: Dict[str, Any]) -> None`
- `__repr__(self) -> str`
- `__eq__(self, other) -> bool`

## Класс MobileSecurityAgentExtra

### Public методы:

#### `__init__(self) -> None`
- **Аргументы**: self
- **Возвращаемое значение**: None
- **Описание**: Инициализация агента

#### `analyze_threat(self, threat_data: ThreatData) -> Dict[str, Any]`
- **Аргументы**: 
  - `self`
  - `threat_data: ThreatData` - данные об угрозе
- **Возвращаемое значение**: `Dict[str, Any]` - результат анализа
- **Описание**: Основной метод анализа угроз

#### `get_status(self) -> Dict[str, Any]` (async)
- **Аргументы**: self
- **Возвращаемое значение**: `Dict[str, Any]` - статус агента
- **Описание**: Получение статуса агента (асинхронный)

#### `cleanup(self) -> None`
- **Аргументы**: self
- **Возвращаемое значение**: None
- **Описание**: Очистка ресурсов

### Private методы:

#### `_init_trusted_apps(self) -> None`
- **Аргументы**: self
- **Возвращаемое значение**: None
- **Описание**: Инициализация базы доверенных приложений

#### `_analyze_threat_trends(self, threat_data: ThreatData) -> Dict[str, Any]`
- **Аргументы**: 
  - `self`
  - `threat_data: ThreatData`
- **Возвращаемое значение**: `Dict[str, Any]`
- **Описание**: Анализ трендов угроз

#### `_get_expert_consensus(self, threat_data: ThreatData) -> float`
- **Аргументы**: 
  - `self`
  - `threat_data: ThreatData`
- **Возвращаемое значение**: `float`
- **Описание**: Получение консенсуса экспертов

#### `_check_whitelists(self, threat_data: ThreatData) -> Dict[str, bool]`
- **Аргументы**: 
  - `self`
  - `threat_data: ThreatData`
- **Возвращаемое значение**: `Dict[str, bool]`
- **Описание**: Проверка белых списков

#### `_check_threat_patterns(self, threat_data: ThreatData) -> Dict[str, Any]`
- **Аргументы**: 
  - `self`
  - `threat_data: ThreatData`
- **Возвращаемое значение**: `Dict[str, Any]`
- **Описание**: Проверка паттернов угроз

#### `_calculate_final_score(self, threat_data, trend_analysis, expert_consensus, whitelist_checks) -> float`
- **Аргументы**: 
  - `self`
  - `threat_data` - данные об угрозе
  - `trend_analysis` - анализ трендов
  - `expert_consensus` - консенсус экспертов
  - `whitelist_checks` - проверки белых списков
- **Возвращаемое значение**: `float`
- **Описание**: Расчет итогового скора

#### `_get_recommendation(self, score: float) -> str`
- **Аргументы**: 
  - `self`
  - `score: float` - скор угрозы
- **Возвращаемое значение**: `str`
- **Описание**: Получение рекомендации

## Проблемы с сигнатурами:

1. **`_calculate_final_score`**: Отсутствуют типы для некоторых параметров
2. **Отсутствуют type hints** для некоторых параметров в private методах