# Документация: compliance/russia_compliance.py

## Общая информация
- **Файл**: compliance/russia_compliance.py
- **Путь**: /Users/sergejhlystov/ALADDIN_NEW/security/vpn/compliance/
- **Размер**: 16KB
- **Строк**: 371
- **Назначение**: Модуль соответствия требованиям 152-ФЗ для ALADDIN VPN

## Описание функций
- `ComplianceStatus` - Enum статусов соответствия 152-ФЗ
- `ComplianceCheck` - Dataclass результата проверки соответствия
- `RussiaComplianceManager` - Основной класс управления соответствием 152-ФЗ
- `check_data_localization()` - Проверка локализации данных
- `check_consent_management()` - Проверка управления согласиями
- `check_data_retention()` - Проверка хранения данных
- `check_security_measures()` - Проверка мер безопасности
- `check_audit_logging()` - Проверка аудита и логирования
- `run_full_compliance_check()` - Запуск полной проверки соответствия

## Импорты
- hashlib
- json
- datetime (datetime, timedelta)
- typing (Dict, List, Optional, Any)
- dataclasses (dataclass)
- enum (Enum)
- logging (std_logging)

## Статус исправления
- **Дата начала**: $(date)
- **Этап**: 1 - ПОДГОТОВКА И АНАЛИЗ
- **Статус**: В процессе