# ИЕРАРХИЯ КЛАССОВ RANSOMWARE PROTECTION SYSTEM

## 📊 ОБЩАЯ СТРУКТУРА

**Всего классов:** 7  
**Уровней наследования:** 2  
**Базовых классов:** 6  
**Наследующих классов:** 1  

## 🏗️ ДЕТАЛЬНАЯ ИЕРАРХИЯ

### 1. БАЗОВЫЕ КЛАССЫ (БЕЗ НАСЛЕДОВАНИЯ)

#### 1.1 FileSystemEventHandler
- **Тип:** Базовый класс
- **Назначение:** Упрощенный обработчик событий файловой системы
- **Методы:** `__init__`, `on_modified`, `on_created`, `on_moved`
- **Атрибуты:** `protection_system`

#### 1.2 Observer
- **Тип:** Базовый класс
- **Назначение:** Упрощенный наблюдатель файловой системы
- **Методы:** `__init__`, `schedule`, `start`, `stop`
- **Атрибуты:** `handlers`

#### 1.3 RansomwareSignature
- **Тип:** Dataclass
- **Назначение:** Сигнатура ransomware атаки
- **Атрибуты:** `name`, `file_extensions`, `suspicious_patterns`, `behavior_indicators`, `risk_level`

#### 1.4 BackupInfo
- **Тип:** Dataclass
- **Назначение:** Информация о резервной копии
- **Атрибуты:** `backup_id`, `timestamp`, `file_path`, `file_hash`, `file_size`, `backup_location`

#### 1.5 RansomwareAlert
- **Тип:** Dataclass
- **Назначение:** Алерт о подозрительной активности
- **Атрибуты:** `alert_id`, `timestamp`, `alert_type`, `severity`, `description`, `affected_files`

#### 1.6 RansomwareProtectionSystem
- **Тип:** Основной класс системы
- **Назначение:** Система защиты от Ransomware
- **Методы:** Множество методов для мониторинга, резервного копирования, сканирования
- **Атрибуты:** `name`, `is_running`, `monitored_directories`, `suspicious_files`, `stats`

### 2. НАСЛЕДУЮЩИЕ КЛАССЫ

#### 2.1 RansomwareFileHandler
- **Тип:** Наследующий класс
- **Базовый класс:** FileSystemEventHandler
- **Назначение:** Обработчик событий файловой системы для обнаружения ransomware
- **Переопределенные методы:** `on_modified`, `on_created`, `on_moved`
- **Дополнительные методы:** `_is_suspicious_file`, `_calculate_file_hash`
- **Атрибуты:** `protection_system`, `logger`

## 🔗 СВЯЗИ МЕЖДУ КЛАССАМИ

### Наследование
```
FileSystemEventHandler
    ↓
RansomwareFileHandler
```

### Композиция
- `RansomwareProtectionSystem` использует `RansomwareFileHandler`
- `RansomwareProtectionSystem` создает объекты `RansomwareSignature`, `BackupInfo`, `RansomwareAlert`
- `RansomwareFileHandler` получает ссылку на `RansomwareProtectionSystem`

### Агрегация
- `Observer` управляет коллекцией `FileSystemEventHandler`
- `RansomwareProtectionSystem` использует `Observer` для мониторинга

## 📋 ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ

1. **Observer Pattern** - `Observer` и `FileSystemEventHandler`
2. **Strategy Pattern** - различные обработчики событий
3. **Data Transfer Object (DTO)** - `RansomwareSignature`, `BackupInfo`, `RansomwareAlert`
4. **Facade Pattern** - `RansomwareProtectionSystem` как единая точка входа

## 🎯 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ

1. **Добавить абстрактные базовые классы** для лучшей типизации
2. **Реализовать интерфейсы** для обработчиков событий
3. **Добавить валидацию** в dataclass объекты
4. **Реализовать специальные методы** (`__str__`, `__repr__`, `__eq__`) для всех классов
5. **Добавить методы контекстного менеджера** для автоматического управления ресурсами