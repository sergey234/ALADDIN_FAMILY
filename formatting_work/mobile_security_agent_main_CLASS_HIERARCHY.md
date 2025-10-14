# Иерархия классов: mobile_security_agent_main.py

## Структура классов

### 1. ThreatType(Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Перечисление типов угроз безопасности
- **Значения**: 9 типов угроз (MALWARE, PHISHING, DATA_LEAK, etc.)

### 2. SecurityThreat (dataclass)
- **Базовый класс**: `object` (через @dataclass)
- **Назначение**: Структура данных для представления угрозы
- **Атрибуты**: 7 полей с типизацией
- **Зависимости**: использует ThreatType

### 3. MobileSecurityAgentMain
- **Базовый класс**: `object` (неявно)
- **Назначение**: Основной класс агента мобильной безопасности
- **Методы**: 15+ методов
- **Зависимости**: использует SecurityThreat, ThreatType

## Иерархия наследования

```
Enum
└── ThreatType

object
├── SecurityThreat (dataclass)
└── MobileSecurityAgentMain
```

## Отношения между классами

- **ThreatType** → используется в **SecurityThreat** (поле threat_type)
- **SecurityThreat** → используется в **MobileSecurityAgentMain** (методы работают с этим типом)
- **MobileSecurityAgentMain** → основной класс системы