# Иерархия классов password_security_agent.py

## Структура классов:

```
object
├── PasswordConfig (dataclass)
├── PasswordStrength (Enum)
├── PasswordStatus (Enum)
├── PasswordPolicy
├── PasswordMetrics
└── SecurityBase
    └── PasswordSecurityAgent
```

## Детальное описание:

### 1. PasswordConfig (dataclass)
- **Базовый класс**: object (через dataclass)
- **Назначение**: Конфигурация агента безопасности паролей
- **Особенности**: Автоматическая генерация __init__, __repr__, __eq__

### 2. PasswordStrength (Enum)
- **Базовый класс**: Enum
- **Назначение**: Уровни сложности пароля
- **Значения**: WEAK, MEDIUM, STRONG, VERY_STRONG

### 3. PasswordStatus (Enum)
- **Базовый класс**: Enum
- **Назначение**: Статусы пароля
- **Значения**: ACTIVE, EXPIRED, COMPROMISED, WEAK, REUSED

### 4. PasswordPolicy
- **Базовый класс**: object
- **Назначение**: Политика безопасности паролей
- **Особенности**: Содержит правила валидации паролей

### 5. PasswordMetrics
- **Базовый класс**: object
- **Назначение**: Метрики агента безопасности паролей
- **Особенности**: Сбор статистики и аналитики

### 6. PasswordSecurityAgent (SecurityBase)
- **Базовый класс**: SecurityBase
- **Назначение**: Основной агент безопасности паролей
- **Особенности**: Главный класс с основной функциональностью

## Полиморфизм:
- Все классы поддерживают строковое представление (__str__)
- PasswordSecurityAgent переопределяет методы базового класса SecurityBase
- Enums поддерживают сравнение и итерацию