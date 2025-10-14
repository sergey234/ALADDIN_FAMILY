# Иерархия классов parent_control_panel.py

## СТРУКТУРА КЛАССОВ

### 1. ENUM КЛАССЫ (Перечисления)
```
Enum
├── ParentRole
│   ├── PRIMARY = "primary"
│   ├── SECONDARY = "secondary" 
│   ├── GUARDIAN = "guardian"
│   └── GRANDPARENT = "grandparent"
├── ChildStatus
│   ├── ACTIVE = "active"
│   ├── RESTRICTED = "restricted"
│   ├── SUSPENDED = "suspended"
│   └── OFFLINE = "offline"
└── NotificationType
    ├── SECURITY_ALERT = "security_alert"
    ├── TIME_LIMIT = "time_limit"
    ├── CONTENT_BLOCK = "content_block"
    ├── LOCATION_UPDATE = "location_update"
    ├── ACHIEVEMENT = "achievement"
    └── EMERGENCY = "emergency"
```

### 2. DATACLASS КЛАССЫ (Структуры данных)
```
@dataclass
├── ChildProfile
│   ├── id: str
│   ├── name: str
│   ├── age: int
│   ├── status: ChildStatus
│   ├── parent_id: str
│   ├── created_at: datetime
│   ├── last_activity: datetime
│   ├── settings: Dict[str, Any]
│   ├── achievements: List[str]
│   ├── time_limits: Dict[str, int]
│   ├── blocked_content: List[str]
│   └── location_history: List[Dict[str, Any]]
├── ParentProfile
│   ├── id: str
│   ├── name: str
│   ├── email: str
│   ├── role: ParentRole
│   ├── children: List[str]
│   ├── created_at: datetime
│   ├── last_login: datetime
│   ├── settings: Dict[str, Any]
│   ├── notifications: Dict[str, bool]
│   └── emergency_contacts: List[str]
└── SecuritySettings
    ├── content_filtering: bool
    ├── time_restrictions: bool
    ├── location_tracking: bool
    ├── app_blocking: bool
    ├── web_filtering: bool
    ├── social_media_monitoring: bool
    ├── emergency_alerts: bool
    └── ai_monitoring: bool
```

### 3. ОСНОВНОЙ КЛАСС (Наследование)
```
SecurityBase
└── ParentControlPanel
    ├── Атрибуты:
    │   ├── color_scheme
    │   ├── parent_profiles
    │   ├── child_profiles
    │   ├── notifications
    │   ├── security_settings
    │   └── ai_models
    └── Методы: (см. анализ методов)
```

## ПРИНЦИПЫ АРХИТЕКТУРЫ

### Наследование
- **ParentControlPanel** наследует от **SecurityBase**
- Использует `super().__init__()` для правильной инициализации
- Переопределяет методы базового класса

### Композиция
- **ParentControlPanel** содержит коллекции:
  - `parent_profiles: Dict[str, ParentProfile]`
  - `child_profiles: Dict[str, ChildProfile]`
  - `notifications: List[Dict]`

### Полиморфизм
- Enum классы обеспечивают типобезопасность
- Dataclass классы обеспечивают структурированные данные
- Основной класс использует полиморфизм через наследование

## ЗАВИСИМОСТИ

### Внешние зависимости
- `SecurityBase` - базовый класс безопасности
- `MatrixAIColorScheme` - цветовая схема
- `ColorTheme` - темы цветов

### Внутренние зависимости
- Все Enum классы используются в dataclass классах
- Dataclass классы используются в основном классе
- Строгая типизация через type hints

## СООТВЕТСТВИЕ SOLID ПРИНЦИПАМ

✅ **Single Responsibility**: Каждый класс имеет одну ответственность
✅ **Open/Closed**: Легко расширяется через наследование
✅ **Liskov Substitution**: ParentControlPanel может заменить SecurityBase
✅ **Interface Segregation**: Четкое разделение интерфейсов
✅ **Dependency Inversion**: Зависит от абстракций, а не от конкретных реализаций