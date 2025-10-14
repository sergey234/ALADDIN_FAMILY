# ДОКУМЕНТАЦИЯ ФАЙЛА: parental_controls.py

## ОСНОВНАЯ ИНФОРМАЦИЯ
- **Путь**: `/Users/sergejhlystov/ALADDIN_NEW/security/family/parental_controls.py`
- **Размер**: 941 строка
- **Версия**: 1.0
- **Дата создания**: 2025-09-02
- **Автор**: ALADDIN Security Team

## НАЗНАЧЕНИЕ
Централизованная система родительского контроля для семейной безопасности в рамках ALADDIN Security System.

## СТРУКТУРА ФАЙЛА
1. **Импорты** (строки 1-15)
2. **Enums** (строки 16-50)
   - ControlType - типы родительского контроля
   - ControlStatus - статус контроля
   - NotificationType - типы уведомлений
3. **Dataclasses** (строки 51-100)
4. **Основной класс ParentalControls** (строки 101-941)

## ЗАВИСИМОСТИ
- `core.base.SecurityBase`
- `core.security_base.SecurityEvent, IncidentSeverity, ThreatType`
- `security.family.family_profile_manager.*`
- `security.family.child_protection.*`
- `security.family.elderly_protection.*`

## ФУНКЦИОНАЛЬНОСТЬ
- Управление правилами родительского контроля
- Фильтрация контента
- Ограничение времени использования
- Контроль приложений
- Отслеживание местоположения
- Экстренный контроль
- Мониторинг общения
- IPv6 защита для детей
- Kill Switch функциональность

## СТАТУС ПРОВЕРКИ
- **Создано**: 2025-01-27
- **Резервная копия**: parental_controls_original_backup.py
- **Готов к анализу**: ✅