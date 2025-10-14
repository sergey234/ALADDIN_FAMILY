# Иерархия классов NetworkSecurityAgent

## Структура классов

### 1. Enum классы (Перечисления)
```
Enum
├── NetworkThreatType
├── NetworkProtocol  
├── ThreatSeverity
└── NetworkStatus
```

### 2. Dataclass классы (Классы данных)
```
@dataclass
├── NetworkPacket
├── NetworkThreat
├── NetworkFlow
├── NetworkAnalysis
└── NetworkMetrics
```

### 3. Основной класс агента
```
SecurityBase
└── NetworkSecurityAgent
```

## Детальное описание

### Enum классы
- **NetworkThreatType**: Типы сетевых угроз (DDoS, PORT_SCAN, BRUTE_FORCE, etc.)
- **NetworkProtocol**: Сетевые протоколы (TCP, UDP, ICMP, HTTP, etc.)
- **ThreatSeverity**: Уровни серьезности угроз (LOW, MEDIUM, HIGH, CRITICAL)
- **NetworkStatus**: Статусы сети (NORMAL, SUSPICIOUS, COMPROMISED, etc.)

### Dataclass классы
- **NetworkPacket**: Сетевой пакет с метаданными
- **NetworkThreat**: Сетевая угроза с индикаторами
- **NetworkFlow**: Сетевой поток с метриками
- **NetworkAnalysis**: Результат анализа сети
- **NetworkMetrics**: Метрики сетевой безопасности

### Основной класс
- **NetworkSecurityAgent**: AI агент сетевой безопасности, наследует от SecurityBase

## Принципы проектирования
- Использование Enum для констант
- Dataclass для структур данных
- Наследование от SecurityBase для интеграции в систему
- Полиморфизм через переопределение методов базового класса