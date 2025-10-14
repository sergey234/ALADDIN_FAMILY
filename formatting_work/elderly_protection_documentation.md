# Документация файла elderly_protection.py

## Общая информация
- **Файл**: `/Users/sergejhlystov/ALADDIN_NEW/security/family/elderly_protection.py`
- **Размер**: 627 строк
- **Назначение**: Специализированная защита пожилых людей от социальной инженерии, мошенничества и обмана
- **Дата анализа**: 2025-01-15

## Структура файла
1. **Импорты** (строки 1-15)
2. **Enums** (строки 17-35)
   - ThreatType - типы угроз для пожилых
   - RiskLevel - уровни риска
   - ProtectionAction - действия защиты
3. **Dataclasses** (строки 37+)
   - ScamPattern - паттерн мошенничества
4. **Основной класс ElderlyProtection**

## Зависимости
- `core.base.SecurityBase`
- `core.security_base.SecurityEvent, SecurityRule, IncidentSeverity`
- `security.family.family_profile_manager.FamilyMember, AgeGroup`
- Стандартные библиотеки: logging, re, time, datetime, typing, dataclasses, enum

## Функциональность
- Защита от телефонного мошенничества
- Защита от email фишинга
- Защита от поддельных сайтов
- Защита от социальной инженерии
- Финансовое мошенничество
- Мошенничество техподдержки
- Медицинское мошенничество
- Лотерейное мошенничество

## Статус интеграции
- Зарегистрирован в SFM (Safe Function Manager)
- Имеет тесты в `/tests/test_elderly_protection.py`
- Интегрирован с семейными функциями
- Используется в родительском контроле