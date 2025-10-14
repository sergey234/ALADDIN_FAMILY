# Документация файла mfa_service.py

## Общая информация
- **Файл**: `/Users/sergejhlystov/ALADDIN_NEW/security/preliminary/mfa_service.py`
- **Размер**: 661 строка
- **Назначение**: Сервис многофакторной аутентификации для семей
- **Версия**: 1.0
- **Дата создания**: 2025-09-02
- **Автор**: ALADDIN Security Team

## Описание
Сервис многофакторной аутентификации (MFA) для системы безопасности ALADDIN. Предоставляет различные методы аутентификации для семейных пользователей с учетом возрастных групп и ролей.

## Основные компоненты

### Enum классы:
- `MFAMethod` - методы аутентификации (SMS, EMAIL, TOTP, PUSH, BIOMETRIC, BACKUP_CODE)
- `MFAStatus` - статусы MFA (PENDING, VERIFIED, EXPIRED, FAILED, BLOCKED)
- `UserRole` - роли пользователей (CHILD, PARENT, ELDERLY, ADMIN)

### Импорты:
- Стандартные библиотеки: logging, time, secrets, hashlib, hmac, base64
- datetime, typing, enum, dataclasses
- Локальные модули: core.base, core.security_base

## Структура файла
- Кодировка: UTF-8
- Строк кода: 661
- Классов: ~7 (по данным из поиска)
- Методов: Множество методов для работы с MFA

## Зависимости
- core.base.SecurityBase
- core.security_base.SecurityEvent, IncidentSeverity, ThreatType

## Статус интеграции
- Зарегистрирован в SFM как function_13
- Статус: Active
- Тип: Preliminary
- Критичность: 🔴 Критично

## Дата создания документации
2025-01-15