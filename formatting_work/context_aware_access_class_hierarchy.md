# ИЕРАРХИЯ КЛАССОВ: context_aware_access.py

## СТРУКТУРА КЛАССОВ

### 1. ENUM КЛАССЫ (4 класса)
- **AccessContext(Enum)** - Контексты доступа
  - HOME, WORK, PUBLIC, MOBILE, UNKNOWN
- **AccessLevel(Enum)** - Уровни доступа  
  - DENIED, RESTRICTED, LIMITED, STANDARD, FULL
- **ContextFactor(Enum)** - Факторы контекста
  - LOCATION, TIME, DEVICE, NETWORK, USER_BEHAVIOR, RISK_LEVEL, TRUST_SCORE, AUTHENTICATION, ENVIRONMENT, ACTIVITY
- **AccessDecisionType(Enum)** - Решения по доступу
  - ALLOW, DENY, CHALLENGE, MONITOR, ESCALATE

### 2. DATACLASS КЛАССЫ (3 класса)
- **ContextData(dataclass)** - Данные контекста
  - user_id, device_id, location, network_type, ip_address, user_agent, timestamp, risk_score, trust_score, authentication_level, activity_type, metadata
- **AccessRule(dataclass)** - Правило доступа
  - rule_id, name, description, context_conditions, access_level, priority, enabled, created_at, updated_at
- **AccessDecision(dataclass)** - Решение по доступу
  - decision_id, user_id, resource, decision, access_level, context_data, applied_rules, confidence_score, reasoning, timestamp, expires_at

### 3. ОСНОВНОЙ КЛАСС (1 класс)
- **ContextAwareAccess(SecurityBase)** - Главный класс системы
  - Наследует от SecurityBase
  - Реализует основную логику контекстно-зависимого доступа

## НАСЛЕДОВАНИЕ И ПОЛИМОРФИЗМ

### Наследование:
- **ContextAwareAccess** наследует от **SecurityBase**
- Все остальные классы не имеют наследования (кроме Enum и dataclass)

### Полиморфизм:
- Enum классы обеспечивают типобезопасность
- Dataclass классы обеспечивают структурированное хранение данных
- ContextAwareAccess реализует полиморфное поведение через методы

## ОТНОШЕНИЯ МЕЖДУ КЛАССАМИ

```
SecurityBase (базовый класс)
    ↓
ContextAwareAccess (основной класс)
    ↓
Использует:
├── AccessContext (enum)
├── AccessLevel (enum) 
├── ContextFactor (enum)
├── AccessDecisionType (enum)
├── ContextData (dataclass)
├── AccessRule (dataclass)
└── AccessDecision (dataclass)
```

## СТАТУС АНАЛИЗА
- **Всего классов**: 8
- **Enum классов**: 4
- **Dataclass классов**: 3  
- **Основных классов**: 1
- **Наследование**: 1 уровень (ContextAwareAccess → SecurityBase)
- **Полиморфизм**: ✅ Реализован через методы