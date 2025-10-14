# 🏗️ ИЕРАРХИЯ КЛАССОВ: Active Network Monitoring v2.5

## 📊 ОБЗОР КЛАССОВ

**Всего классов**: 9  
**Enum классов**: 4  
**Dataclass классов**: 4  
**Основной сервис**: 1  

## 🔍 ДЕТАЛЬНАЯ ИЕРАРХИЯ

### 1. ENUM КЛАССЫ (4 класса)

#### 1.1 NetworkType(Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Типы сетей
- **Значения**: WIFI, ETHERNET, MOBILE, BLUETOOTH, VPN, UNKNOWN
- **MRO**: NetworkType → Enum → object

#### 1.2 TrafficType(Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Типы трафика
- **Значения**: WEB, EMAIL, GAMING, SOCIAL_MEDIA, STREAMING, DOWNLOAD, UPLOAD, CHAT, FILE_SHARING, UNKNOWN
- **MRO**: TrafficType → Enum → object

#### 1.3 ThreatLevel(Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Уровни угроз
- **Значения**: LOW, MEDIUM, HIGH, CRITICAL
- **MRO**: ThreatLevel → Enum → object

#### 1.4 MonitoringAction(Enum)
- **Базовый класс**: `Enum`
- **Назначение**: Действия мониторинга
- **Значения**: LOG, ALERT, BLOCK, THROTTLE, QUARANTINE, NOTIFY_PARENT, NOTIFY_ADMIN, SCAN_DEEP
- **MRO**: MonitoringAction → Enum → object

### 2. DATACLASS КЛАССЫ (4 класса)

#### 2.1 NetworkConnection(dataclass)
- **Базовый класс**: `object`
- **Назначение**: Сетевое соединение
- **Атрибуты**: 15 полей (connection_id, source_ip, destination_ip, etc.)
- **MRO**: NetworkConnection → object

#### 2.2 NetworkAnomaly(dataclass)
- **Базовый класс**: `object`
- **Назначение**: Сетевая аномалия
- **Атрибуты**: 10 полей (anomaly_id, connection_id, anomaly_type, etc.)
- **MRO**: NetworkAnomaly → object

#### 2.3 NetworkRule(dataclass)
- **Базовый класс**: `object`
- **Назначение**: Правило мониторинга сети
- **Атрибуты**: 8 полей (rule_id, name, description, etc.)
- **MRO**: NetworkRule → object

#### 2.4 NetworkStatistics(dataclass)
- **Базовый класс**: `object`
- **Назначение**: Статистика сети
- **Атрибуты**: 10 полей (total_connections, total_bytes_sent, etc.)
- **MRO**: NetworkStatistics → object

### 3. ОСНОВНОЙ СЕРВИС (1 класс)

#### 3.1 NetworkMonitoringService(SecurityBase)
- **Базовый класс**: `SecurityBase`
- **Назначение**: Сервис мониторинга сетевой активности для семей
- **MRO**: NetworkMonitoringService → SecurityBase → CoreBase → ABC → object
- **Интеграция**: Наследует от SecurityBase для интеграции с системой безопасности

## 🔗 СВЯЗИ МЕЖДУ КЛАССАМИ

### Наследование:
```
object
├── Enum
│   ├── NetworkType
│   ├── TrafficType
│   ├── ThreatLevel
│   └── MonitoringAction
├── NetworkConnection (dataclass)
├── NetworkAnomaly (dataclass)
├── NetworkRule (dataclass)
├── NetworkStatistics (dataclass)
└── SecurityBase
    └── NetworkMonitoringService
```

### Зависимости:
- **NetworkMonitoringService** использует все Enum классы
- **NetworkMonitoringService** создает экземпляры всех dataclass классов
- **NetworkConnection** используется в **NetworkAnomaly**
- **NetworkRule** определяет правила для **NetworkMonitoringService**

## 🎯 АРХИТЕКТУРНЫЕ ПРИНЦИПЫ

### 1. SOLID Принципы:
- **S (Single Responsibility)**: Каждый класс имеет одну ответственность
- **O (Open/Closed)**: Enum классы легко расширяемы
- **L (Liskov Substitution)**: Наследование от SecurityBase корректно
- **I (Interface Segregation)**: Четкое разделение интерфейсов
- **D (Dependency Inversion)**: Зависимость от абстракций (SecurityBase)

### 2. Паттерны проектирования:
- **Dataclass**: Для структур данных
- **Enum**: Для констант
- **Service**: Для бизнес-логики
- **Inheritance**: Для расширения функциональности

### 3. Семейная безопасность:
- **Специализированные Enum**: Для семейных сценариев
- **Dataclass с метаданными**: Для отслеживания пользователей
- **Интеграция с SecurityBase**: Для единой системы безопасности

## ✅ КАЧЕСТВО АРХИТЕКТУРЫ

- **Модульность**: Высокая ✅
- **Расширяемость**: Высокая ✅
- **Тестируемость**: Высокая ✅
- **Читаемость**: Высокая ✅
- **Производительность**: Оптимальная ✅

## 🚀 ГОТОВНОСТЬ К РАСШИРЕНИЮ

- **Новые типы сетей**: Легко добавить в NetworkType
- **Новые типы трафика**: Легко добавить в TrafficType
- **Новые действия**: Легко добавить в MonitoringAction
- **Новые правила**: Легко добавить в NetworkRule
- **Новые метрики**: Легко добавить в NetworkStatistics

## 📈 ИТОГОВАЯ ОЦЕНКА АРХИТЕКТУРЫ

**ОБЩАЯ ОЦЕНКА: A+ (ОТЛИЧНО)**

- ✅ Четкая иерархия классов
- ✅ Правильное использование наследования
- ✅ Соответствие SOLID принципам
- ✅ Готовность к расширению
- ✅ Интеграция с системой безопасности