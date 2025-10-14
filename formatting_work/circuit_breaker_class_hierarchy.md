# Иерархия классов circuit_breaker.py

## Структура наследования

```
Enum
└── CircuitState
    ├── CLOSED = "closed"
    ├── OPEN = "open"
    └── HALF_OPEN = "half_open"

dataclass
└── CircuitBreakerConfig
    ├── failure_threshold: int = 5
    ├── success_threshold: int = 3
    ├── timeout: float = 60.0
    ├── adaptive_threshold: bool = True
    ├── min_failure_threshold: int = 3
    ├── max_failure_threshold: int = 20
    ├── min_calls_for_analysis: int = 10
    ├── error_rate_threshold: float = 0.5
    ├── consecutive_errors: int = 3
    ├── recovery_timeout: float = 30.0
    └── max_recovery_timeout: float = 300.0

SmartCircuitBreaker (базовый класс)
├── Атрибуты:
│   ├── name: str
│   ├── config: CircuitBreakerConfig
│   ├── state: CircuitState
│   ├── failure_count: int
│   ├── success_count: int
│   ├── call_history: List[bool]
│   ├── response_times: List[float]
│   ├── last_failure_time: Optional[datetime]
│   └── last_success_time: Optional[datetime]
└── Методы: (см. раздел 6.2)

Exception
└── CircuitBreakerOpenException
    └── pass (простое исключение)
```

## Полиморфизм

1. **CircuitState** - полиморфизм через перечисление состояний
2. **CircuitBreakerOpenException** - полиморфизм исключений
3. **SmartCircuitBreaker** - не использует полиморфизм (базовый класс)

## Отношения между классами

- `SmartCircuitBreaker` использует `CircuitBreakerConfig` (композиция)
- `SmartCircuitBreaker` использует `CircuitState` (агрегация)
- `SmartCircuitBreaker` может вызывать `CircuitBreakerOpenException` (ассоциация)

## Дата создания документации
2025-01-27