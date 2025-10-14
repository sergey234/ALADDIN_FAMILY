# Иерархия классов elderly_protection.py

## Структура классов

### 1. Enum классы (Перечисления)
- **ThreatType(Enum)** - Типы угроз для пожилых
  - Базовый класс: `Enum`
  - Значения: PHONE_SCAM, EMAIL_PHISHING, FAKE_WEBSITE, SOCIAL_ENGINEERING, FINANCIAL_FRAUD, TECH_SUPPORT_SCAM, MEDICAL_SCAM, LOTTERY_SCAM

- **RiskLevel(Enum)** - Уровни риска
  - Базовый класс: `Enum`
  - Значения: LOW, MEDIUM, HIGH, CRITICAL

- **ProtectionAction(Enum)** - Действия защиты
  - Базовый класс: `Enum`
  - Значения: ALLOW, WARN, BLOCK, NOTIFY_FAMILY, EMERGENCY_CONTACT

### 2. Dataclass классы (Структуры данных)
- **ScamPattern** - Паттерн мошенничества
  - Базовый класс: `object` (через @dataclass)
  - Атрибуты: pattern_id, threat_type, keywords, phone_patterns, email_patterns, website_patterns, risk_level, description

- **ElderlyActivity** - Активность пожилого человека
  - Базовый класс: `object` (через @dataclass)
  - Атрибуты: activity_id, elderly_id, activity_type, content, source, timestamp, threat_detected, risk_level, action_taken, family_notified

- **FamilyContact** - Контакт семьи для уведомлений
  - Базовый класс: `object` (через @dataclass)
  - Атрибуты: contact_id, name, phone, email, relationship, priority

### 3. Основной класс
- **ElderlyProtection(SecurityBase)** - Защита пожилых людей
  - Базовый класс: `SecurityBase`
  - Наследование: Правильно реализовано через super().__init__()
  - Полиморфизм: Переопределяет методы базового класса

## Связи между классами
- `ElderlyProtection` использует `ScamPattern`, `ElderlyActivity`, `FamilyContact`
- `ScamPattern` использует `ThreatType` и `RiskLevel`
- `ElderlyActivity` использует `ThreatType`, `RiskLevel`, `ProtectionAction`
- `FamilyContact` - независимый класс

## Архитектурные принципы
- ✅ SOLID принципы соблюдены
- ✅ Наследование реализовано корректно
- ✅ Полиморфизм используется правильно
- ✅ Инкапсуляция через private методы (_initialize_scam_patterns)
- ✅ Композиция через использование других классов