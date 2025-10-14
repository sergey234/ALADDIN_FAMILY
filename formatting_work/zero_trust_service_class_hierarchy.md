# Иерархия классов zero_trust_service.py

## СТРУКТУРА НАСЛЕДОВАНИЯ

### 1. Enum классы (Перечисления)
```
Enum
├── TrustLevel
│   ├── UNTRUSTED
│   ├── LOW
│   ├── MEDIUM
│   ├── HIGH
│   └── FULL
├── AccessDecision
│   ├── ALLOW
│   ├── DENY
│   ├── CHALLENGE
│   └── MONITOR
├── DeviceType
│   ├── MOBILE
│   ├── TABLET
│   ├── DESKTOP
│   ├── LAPTOP
│   ├── SMART_TV
│   └── IOT
└── NetworkType
    ├── HOME
    ├── WORK
    ├── PUBLIC
    └── UNKNOWN
```

### 2. Dataclass классы (Структуры данных)
```
object
├── DeviceProfile
│   ├── device_id: str
│   ├── device_name: str
│   ├── device_type: DeviceType
│   ├── user_id: str
│   ├── family_id: str
│   ├── mac_address: str
│   ├── ip_address: str
│   ├── os_version: str
│   ├── app_version: str
│   ├── last_seen: datetime
│   ├── trust_score: float
│   ├── is_trusted: bool
│   ├── security_patches: List[str]
│   └── installed_apps: List[str]
├── AccessRequest
│   ├── request_id: str
│   ├── user_id: str
│   ├── device_id: str
│   ├── resource: str
│   ├── action: str
│   ├── context: Dict[str, Any]
│   ├── timestamp: datetime
│   ├── network_type: NetworkType
│   ├── location: Optional[str]
│   └── risk_score: float
└── AccessPolicy
    ├── policy_id: str
    ├── name: str
    ├── description: str
    ├── resource_pattern: str
    ├── user_conditions: Dict[str, Any]
    ├── device_conditions: Dict[str, Any]
    ├── network_conditions: Dict[str, Any]
    ├── time_conditions: Dict[str, Any]
    ├── trust_requirements: TrustLevel
    ├── action: AccessDecision
    ├── is_active: bool
    └── created_at: datetime
```

### 3. Основной сервисный класс
```
SecurityBase
└── ZeroTrustService
    ├── __init__(self, config: Optional[Dict[str, Any]] = None)
    ├── register_device(...)
    ├── update_device_trust(...)
    ├── evaluate_access_request(...)
    ├── block_device(...)
    ├── unblock_device(...)
    ├── get_device_trust_report(...)
    ├── get_status(...)
    └── [приватные методы]
```

## ПРИНЦИПЫ АРХИТЕКТУРЫ

### Наследование
- **Enum классы**: Наследуют от `Enum` для создания перечислений
- **Dataclass классы**: Используют `@dataclass` декоратор для автоматической генерации методов
- **ZeroTrustService**: Наследует от `SecurityBase` для интеграции с системой безопасности

### Полиморфизм
- Все Enum классы поддерживают полиморфное поведение через наследование от `Enum`
- `ZeroTrustService` может использоваться как `SecurityBase` благодаря наследованию
- Dataclass классы поддерживают полиморфизм через типизацию

### Инкапсуляция
- Публичные методы: `register_device`, `update_device_trust`, `evaluate_access_request`
- Приватные методы: `_apply_access_policies`, `_calculate_risk`, `_determine_network_type`
- Защищенные атрибуты: все атрибуты dataclass классов

## СООТВЕТСТВИЕ SOLID ПРИНЦИПАМ

### Single Responsibility Principle (SRP)
- ✅ Каждый класс имеет одну ответственность
- ✅ `TrustLevel` - только уровни доверия
- ✅ `DeviceProfile` - только профиль устройства
- ✅ `ZeroTrustService` - только логика Zero Trust

### Open/Closed Principle (OCP)
- ✅ Классы открыты для расширения через наследование
- ✅ Enum классы можно расширять новыми значениями
- ✅ `ZeroTrustService` можно расширять новыми методами

### Liskov Substitution Principle (LSP)
- ✅ `ZeroTrustService` может заменить `SecurityBase`
- ✅ Все Enum классы взаимозаменяемы в своих контекстах

### Interface Segregation Principle (ISP)
- ✅ Интерфейсы разделены по функциональности
- ✅ Каждый dataclass содержит только необходимые поля

### Dependency Inversion Principle (DIP)
- ✅ `ZeroTrustService` зависит от абстракции `SecurityBase`
- ✅ Использует типизацию для зависимостей