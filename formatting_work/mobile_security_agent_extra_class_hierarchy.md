# Иерархия классов mobile_security_agent_extra.py

## Структура классов

### 1. ThreatData (dataclass)
```
object
  └── ThreatData (dataclass)
```

**Описание**: Структура данных для хранения информации об угрозе
**Атрибуты**:
- `app_id: str` - идентификатор приложения
- `threat_type: str` - тип угрозы
- `severity: str` - уровень серьезности
- `confidence: float` - уровень уверенности
- `timestamp: datetime` - временная метка
- `details: Dict[str, Any]` - дополнительные детали

### 2. MobileSecurityAgentExtra (класс)
```
object
  └── MobileSecurityAgentExtra
```

**Описание**: Основной класс агента мобильной безопасности
**Атрибуты**:
- `logger` - логгер для записи событий
- `trusted_apps_database` - база доверенных приложений
- `threat_patterns` - паттерны угроз
- `expert_consensus` - консенсус экспертов
- `lock` - блокировка для многопоточности
- `stats` - статистика работы

## Отношения между классами

- `MobileSecurityAgentExtra` использует `ThreatData` как параметр в методах
- Нет прямого наследования между классами
- Отношение "использует" (composition)

## Особенности архитектуры

1. **Dataclass**: `ThreatData` использует @dataclass для автоматической генерации методов
2. **Threading**: `MobileSecurityAgentExtra` использует threading.Lock для безопасности
3. **Logging**: Интегрированное логирование для отслеживания событий
4. **Singleton pattern**: Глобальный экземпляр `mobile_security_agent_extra`