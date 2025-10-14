# Документация файла zero_trust_service.py

## Общая информация
- **Файл**: `/Users/sergejhlystov/ALADDIN_NEW/security/preliminary/zero_trust_service.py`
- **Размер**: 687 строк
- **Тип**: Python модуль
- **Назначение**: Упрощенная Zero Trust архитектура для семей

## Структура файла
- **Импорты**: 8 внешних модулей + 2 внутренних
- **Классы**: 6 основных классов (TrustLevel, AccessDecision, DeviceType, NetworkType, DeviceProfile, ZeroTrustService)
- **Функции**: Множество методов для управления доверием и доступом

## Основные компоненты
1. **TrustLevel** - Уровни доверия (UNTRUSTED, LOW, MEDIUM, HIGH, FULL)
2. **AccessDecision** - Решения по доступу (ALLOW, DENY, CHALLENGE, MONITOR)
3. **DeviceType** - Типы устройств (MOBILE, TABLET, DESKTOP, LAPTOP, SMART_TV, IOT)
4. **NetworkType** - Типы сетей (HOME, PUBLIC, CORPORATE, UNKNOWN)
5. **DeviceProfile** - Профиль устройства с метаданными
6. **ZeroTrustService** - Основной сервис управления доверием

## Зависимости
- **Внешние**: logging, time, hashlib, datetime, typing, enum, dataclasses
- **Внутренние**: core.base, core.security_base

## Дата создания документации
2025-01-15 12:00:00