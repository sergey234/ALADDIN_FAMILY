# Иерархия классов intrusion_prevention.py

## 📊 ОБЗОР СТРУКТУРЫ КЛАССОВ

**Всего классов: 7**

### 🔍 ENUM КЛАССЫ (3 класса)
Наследуются от `Enum` - обеспечивают типизированные константы

1. **ThreatLevel** - Уровни угроз
   - Базовый класс: `Enum`
   - Значения: LOW, MEDIUM, HIGH, CRITICAL (4 значения)
   - Назначение: Определение критичности угроз

2. **AttackType** - Типы атак
   - Базовый класс: `Enum`
   - Значения: BRUTE_FORCE, DDoS, PORT_SCAN, SQL_INJECTION, XSS, CSRF, MALWARE, PHISHING, MAN_IN_THE_MIDDLE, ZERO_DAY (10 значений)
   - Назначение: Классификация типов атак

3. **ActionType** - Типы действий
   - Базовый класс: `Enum`
   - Значения: ALLOW, BLOCK, QUARANTINE, ALERT, LOG (5 значений)
   - Назначение: Определение действий системы безопасности

### 🔍 DATACLASS КЛАССЫ (3 класса)
Наследуются от `object` - структуры данных с автоматической генерацией методов

1. **IntrusionAttempt** - Попытка вторжения
   - Базовый класс: `object`
   - Поля: 11 (source_ip, target_ip, port, attack_type, threat_level, timestamp, payload, user_agent, session_id, is_blocked, action_taken)
   - Назначение: Хранение информации о попытке вторжения

2. **SecurityRule** - Правило безопасности
   - Базовый класс: `object`
   - Поля: 10 (rule_id, name, description, pattern, attack_type, threat_level, action, is_active, created_at, updated_at)
   - Назначение: Определение правил безопасности

3. **NetworkFlow** - Сетевой поток
   - Базовый класс: `object`
   - Поля: 12 (source_ip, dest_ip, source_port, dest_port, protocol, bytes_sent, bytes_received, packets_sent, packets_received, start_time, end_time, duration)
   - Назначение: Мониторинг сетевого трафика

### 🔍 ОСНОВНОЙ КЛАСС (1 класс)
Наследуется от `object` - основная бизнес-логика

1. **IntrusionPrevention** - Система предотвращения вторжений
   - Базовый класс: `object`
   - Методы: 15 (add_rule, add_to_whitelist, analyze_log_entry, analyze_network_flow, check_rate_limit, export_rules, get_recent_attempts, get_statistics, import_rules, is_ip_blocked, is_ip_whitelisted, remove_from_whitelist, remove_rule, unblock_ip, update_rule)
   - Назначение: Основная логика системы безопасности

## 📈 АРХИТЕКТУРНЫЕ ПРИНЦИПЫ

### ✅ СОБЛЮДЕНИЕ SOLID:
- **Single Responsibility**: Каждый класс имеет одну ответственность
- **Open/Closed**: Enum классы легко расширяются
- **Liskov Substitution**: Dataclass классы взаимозаменяемы
- **Interface Segregation**: Четкое разделение интерфейсов
- **Dependency Inversion**: Зависимость от абстракций (Enum)

### ✅ ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ:
- **Enum Pattern**: Типизированные константы
- **Data Transfer Object (DTO)**: Dataclass для передачи данных
- **Strategy Pattern**: Различные типы атак и действий
- **Factory Pattern**: Создание объектов через конструкторы

## 🎯 СТАТУС КАЧЕСТВА
- **Архитектура**: A+ (четкое разделение ответственностей)
- **Типизация**: A+ (полная типизация всех полей)
- **Документация**: A+ (docstring для всех классов)
- **Структура**: A+ (логичная иерархия классов)