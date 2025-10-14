# ИЕРАРХИЯ КЛАССОВ SECURITY MONITORING A+ SYSTEM

## 📊 СТРУКТУРА КЛАССОВ

### 1. Перечисления (Enums)
- **MonitoringLevel(Enum)** - Уровни мониторинга безопасности
- **AlertType(Enum)** - Типы алертов безопасности

### 2. Dataclasses
- **SecurityEvent** - Событие безопасности
- **MonitoringConfig** - Конфигурация мониторинга

### 3. Абстрактные классы
- **IMonitoringStrategy(ABC)** - Интерфейс стратегии мониторинга

### 4. Базовые классы
- **BaseSecurityStrategy(IMonitoringStrategy)** - Базовая стратегия безопасности

### 5. Конкретные стратегии
- **ThreatDetectionStrategy(BaseSecurityStrategy)** - Стратегия обнаружения угроз
- **AnomalyDetectionStrategy(BaseSecurityStrategy)** - Стратегия обнаружения аномалий

### 6. Менеджеры
- **MonitoringDataManager** - Менеджер данных мониторинга
- **AlertManager** - Менеджер алертов

### 7. Основной класс
- **SecurityMonitoringManager(SecurityBase)** - Главный менеджер мониторинга

## 🔗 СХЕМА НАСЛЕДОВАНИЯ

```
Enum
├── MonitoringLevel
└── AlertType

ABC
└── IMonitoringStrategy
    └── BaseSecurityStrategy
        ├── ThreatDetectionStrategy
        └── AnomalyDetectionStrategy

SecurityBase
└── SecurityMonitoringManager

Dataclasses (независимые)
├── SecurityEvent
└── MonitoringConfig

Utility Classes (независимые)
├── MonitoringDataManager
└── AlertManager
```

## 🎯 ПРИНЦИПЫ SOLID

### Single Responsibility Principle (SRP)
- **MonitoringLevel**: Только уровни мониторинга
- **AlertType**: Только типы алертов
- **SecurityEvent**: Только данные события
- **MonitoringConfig**: Только конфигурация
- **ThreatDetectionStrategy**: Только обнаружение угроз
- **AnomalyDetectionStrategy**: Только обнаружение аномалий
- **MonitoringDataManager**: Только управление данными
- **AlertManager**: Только управление алертами
- **SecurityMonitoringManager**: Только координация мониторинга

### Open/Closed Principle (OCP)
- **IMonitoringStrategy**: Открыт для расширения новыми стратегиями
- **BaseSecurityStrategy**: Закрыт для модификации, открыт для расширения

### Liskov Substitution Principle (LSP)
- **ThreatDetectionStrategy** и **AnomalyDetectionStrategy** взаимозаменяемы
- Все стратегии могут использоваться вместо **IMonitoringStrategy**

### Interface Segregation Principle (ISP)
- **IMonitoringStrategy**: Минимальный интерфейс для стратегий
- Отдельные интерфейсы для разных типов функциональности

### Dependency Inversion Principle (DIP)
- **SecurityMonitoringManager** зависит от абстракции **IMonitoringStrategy**
- Не зависит от конкретных реализаций стратегий

## ✅ ПРОВЕРКА ПОЛИМОРФИЗМА

### Стратегии мониторинга
- Все стратегии реализуют `check_security()` метод
- Все стратегии имеют `get_strategy_name()` метод
- Полиморфное поведение через общий интерфейс

### Менеджеры
- **MonitoringDataManager** и **AlertManager** работают независимо
- Общая конфигурация через **MonitoringConfig**

## 📈 КАЧЕСТВО АРХИТЕКТУРЫ

- **Модульность**: Высокая - каждый класс имеет четкую ответственность
- **Расширяемость**: Высокая - легко добавить новые стратегии
- **Тестируемость**: Высокая - каждый компонент можно тестировать отдельно
- **Поддерживаемость**: Высокая - четкое разделение ответственности