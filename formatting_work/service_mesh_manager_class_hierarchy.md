# Иерархия классов ServiceMeshManager

## СТРУКТУРА КЛАССОВ

### 1. Перечисления (Enums)
```
Enum (базовый класс)
├── ServiceStatus
│   ├── HEALTHY
│   ├── UNHEALTHY
│   ├── DEGRADED
│   ├── STARTING
│   ├── STOPPING
│   └── UNKNOWN
├── ServiceType
│   ├── SECURITY
│   ├── AI_AGENT
│   ├── BOT
│   ├── INTERFACE
│   ├── DATABASE
│   ├── CACHE
│   ├── API
│   └── MONITORING
└── LoadBalancingStrategy
    ├── ROUND_ROBIN
    ├── LEAST_CONNECTIONS
    ├── WEIGHTED_ROUND_ROBIN
    ├── LEAST_RESPONSE_TIME
    └── RANDOM
```

### 2. Модели данных (@dataclass)
```
object (базовый класс)
├── ServiceEndpoint
│   ├── service_id: str
│   ├── host: str
│   ├── port: int
│   ├── protocol: str
│   ├── path: str
│   ├── weight: int = 1
│   ├── health_check_url: Optional[str] = None
│   ├── last_health_check: Optional[datetime] = None
│   ├── is_healthy: bool = True
│   ├── to_dict() -> Dict[str, Any]
│   └── get_url() -> str
├── ServiceInfo
│   ├── service_id: str
│   ├── name: str
│   ├── description: str
│   ├── service_type: ServiceType
│   ├── version: str
│   ├── endpoints: List[ServiceEndpoint]
│   ├── dependencies: List[str]
│   ├── health_check_interval: int = 30
│   ├── timeout: int = 30
│   ├── retry_count: int = 3
│   ├── status: ServiceStatus = ServiceStatus.UNKNOWN
│   ├── created_at: Optional[datetime] = None
│   ├── last_updated: Optional[datetime] = None
│   ├── __post_init__()
│   └── to_dict() -> Dict[str, Any]
├── ServiceRequest
│   ├── request_id: str
│   ├── service_id: str
│   ├── method: str
│   ├── path: str
│   ├── headers: Dict[str, str]
│   ├── body: Optional[Any] = None
│   ├── timeout: int = 30
│   ├── retry_count: int = 0
│   ├── created_at: Optional[datetime] = None
│   ├── __post_init__()
│   └── to_dict() -> Dict[str, Any]
└── ServiceResponse
    ├── request_id: str
    ├── service_id: str
    ├── status_code: int
    ├── headers: Dict[str, str]
    ├── body: Optional[Any] = None
    ├── response_time: float = 0.0
    ├── error_message: Optional[str] = None
    ├── created_at: Optional[datetime] = None
    ├── __post_init__()
    └── to_dict() -> Dict[str, Any]
```

### 3. Основной класс
```
SecurityBase (базовый класс)
└── ServiceMeshManager
    ├── __init__(name: str, config: Optional[Dict[str, Any]])
    ├── initialize() -> bool
    ├── register_service(service: ServiceInfo) -> bool
    ├── unregister_service(service_id: str) -> bool
    ├── get_service_endpoint(service_id: str) -> Optional[ServiceEndpoint]
    ├── send_request(...) -> Optional[ServiceResponse]
    ├── get_service_status(service_id: str) -> Optional[Dict[str, Any]]
    ├── get_mesh_status() -> Dict[str, Any]
    ├── stop() -> bool
    └── get_status() -> Dict[str, Any]
```

## ОТНОШЕНИЯ МЕЖДУ КЛАССАМИ

1. **ServiceMeshManager** использует все enum классы для типизации
2. **ServiceMeshManager** работает с объектами ServiceInfo, ServiceEndpoint, ServiceRequest, ServiceResponse
3. **ServiceInfo** содержит список ServiceEndpoint
4. **ServiceRequest** и **ServiceResponse** связаны через request_id
5. Все @dataclass классы имеют метод to_dict() для сериализации

## НАСЛЕДОВАНИЕ

- **ServiceMeshManager** наследует от SecurityBase (из core.base)
- **Enum классы** наследуют от Enum (стандартная библиотека)
- **@dataclass классы** наследуют от object (неявно)

## ПОЛИМОРФИЗМ

- Переопределение методов базового класса SecurityBase
- Использование enum значений для типизации
- Методы to_dict() во всех @dataclass классах