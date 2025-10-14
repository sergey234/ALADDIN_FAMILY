# ИЕРАРХИЯ КЛАССОВ: gaming_security_bot.py

## ОБЩАЯ СТРУКТУРА
**Всего классов**: 12
**Типы классов**:
- Enum классы: 4
- SQLAlchemy модели: 4  
- Pydantic модели: 3
- Основной класс: 1

## ДЕТАЛЬНАЯ ИЕРАРХИЯ

### 1. ENUM КЛАССЫ (4 класса)
```
Enum (базовый класс Python)
├── CheatType
│   ├── AIMBOT = "aimbot"
│   ├── WALLHACK = "wallhack"
│   ├── SPEEDHACK = "speedhack"
│   ├── TELEPORT = "teleport"
│   ├── INVISIBILITY = "invisibility"
│   ├── DAMAGE_HACK = "damage_hack"
│   ├── HEALTH_HACK = "health_hack"
│   ├── RESOURCE_HACK = "resource_hack"
│   ├── MACRO = "macro"
│   ├── BOT = "bot"
│   └── UNKNOWN = "unknown"
├── ThreatLevel
│   ├── LOW = "low"
│   ├── MEDIUM = "medium"
│   ├── HIGH = "high"
│   ├── CRITICAL = "critical"
│   └── IMMEDIATE = "immediate"
├── GameGenre
│   ├── FPS = "fps"
│   ├── RPG = "rpg"
│   ├── STRATEGY = "strategy"
│   ├── MOBA = "moba"
│   ├── BATTLE_ROYALE = "battle_royale"
│   ├── RACING = "racing"
│   ├── PUZZLE = "puzzle"
│   ├── SPORTS = "sports"
│   ├── SIMULATION = "simulation"
│   └── ADVENTURE = "adventure"
└── PlayerAction
    ├── MOVE = "move"
    ├── SHOOT = "shoot"
    ├── JUMP = "jump"
    ├── CROUCH = "crouch"
    ├── RELOAD = "reload"
    ├── SWITCH_WEAPON = "switch_weapon"
    ├── CHAT = "chat"
    ├── PURCHASE = "purchase"
    ├── LOGIN = "login"
    └── LOGOUT = "logout"
```

### 2. SQLALCHEMY МОДЕЛИ (4 класса)
```
Base (declarative_base)
├── GameSession
│   ├── Таблица: "game_sessions"
│   ├── Поля: id, player_id, game_id, game_genre, start_time, end_time, duration, score, kills, deaths, assists, suspicious_actions, cheat_detected, ban_applied, created_at
│   └── Назначение: Хранение игровых сессий
├── CheatDetection
│   ├── Таблица: "cheat_detections"
│   ├── Поля: id, session_id, player_id, cheat_type, confidence, evidence, threat_level, action_taken, timestamp, reviewed
│   └── Назначение: Хранение детекций читов
├── PlayerBehavior
│   ├── Таблица: "player_behaviors"
│   ├── Поля: id, player_id, session_id, action_type, coordinates, timestamp, reaction_time, accuracy, suspicious_score, context
│   └── Назначение: Хранение поведения игроков
└── GameTransaction
    ├── Таблица: "game_transactions"
    ├── Поля: id, player_id, session_id, transaction_type, amount, currency, item_id, payment_method, is_fraudulent, risk_score, timestamp
    └── Назначение: Хранение игровых транзакций
```

### 3. PYDANTIC МОДЕЛИ (3 класса)
```
BaseModel (Pydantic)
├── SecurityAlert
│   ├── Поля: alert_id, player_id, session_id, alert_type, threat_level, description, evidence, action_required, timestamp, auto_resolved
│   └── Назначение: Валидация оповещений безопасности
├── CheatAnalysisResult
│   ├── Поля: cheat_type, confidence, threat_level, evidence, recommended_action, false_positive_probability
│   └── Назначение: Валидация результатов анализа читов
└── PlayerProfile
    ├── Поля: player_id, username, reputation_score, total_playtime, games_played, cheats_detected, bans_received, last_activity, risk_level, behavior_patterns
    └── Назначение: Валидация профилей игроков
```

### 4. ОСНОВНОЙ КЛАСС (1 класс)
```
SecurityBase (core.base)
└── GamingSecurityBot
    ├── Основной функционал бота безопасности игр
    ├── Методы: Анализ читов, мониторинг, транзакции, профили
    └── Интеграция с ML моделями и базами данных
```

## АНАЛИЗ НАСЛЕДОВАНИЯ

### ПОЛИМОРФИЗМ
- **Enum классы**: Используют полиморфизм для типизации значений
- **SQLAlchemy модели**: Наследуют от Base для ORM функциональности
- **Pydantic модели**: Наследуют от BaseModel для валидации данных
- **GamingSecurityBot**: Наследует от SecurityBase для базовой безопасности

### СООТВЕТСТВИЕ SOLID ПРИНЦИПАМ
- ✅ **Single Responsibility**: Каждый класс имеет одну ответственность
- ✅ **Open/Closed**: Enum классы легко расширяются
- ✅ **Liskov Substitution**: Все модели могут быть заменены базовыми
- ✅ **Interface Segregation**: Четкое разделение интерфейсов
- ✅ **Dependency Inversion**: Использование абстракций (Base, BaseModel)

## МЕТРИКИ
- **Всего классов**: 12
- **Enum значений**: 40
- **Поля баз данных**: 31
- **Pydantic поля**: 30
- **Строки кода классов**: ~200 строк