# Документация файла emergency_contact_manager.py

## Общая информация
- **Путь**: `/Users/sergejhlystov/ALADDIN_NEW/security/ai_agents/emergency_contact_manager.py`
- **Размер**: 280 строк
- **Тип**: Python модуль
- **Назначение**: Менеджер контактов экстренного реагирования

## Описание
Модуль реализует менеджер контактов для экстренного реагирования с применением принципа Single Responsibility. Предоставляет функциональность для управления контактами, их группировки и получения контактов для экстренных ситуаций.

## Основные классы
- `EmergencyContactManager` - основной класс менеджера контактов

## Основные методы
- `add_contact()` - добавление нового контакта
- `get_contact()` - получение контакта по ID
- `update_contact()` - обновление контакта
- `delete_contact()` - удаление контакта
- `get_contacts_by_priority()` - получение контактов по приоритету
- `get_available_contacts()` - получение доступных контактов
- `get_contacts_by_relationship()` - получение контактов по отношению
- `create_contact_group()` - создание группы контактов
- `get_contact_group()` - получение контактов группы
- `get_emergency_contacts()` - получение контактов для экстренной ситуации
- `get_contact_statistics()` - получение статистики контактов

## Зависимости
- `logging` - для логирования
- `typing` - для типизации
- `.emergency_models` - модели данных
- `.emergency_id_generator` - генератор ID
- `.emergency_validators` - валидаторы

## Архитектурные принципы
- Single Responsibility Principle
- Типизация с использованием typing
- Обработка исключений
- Логирование операций

## Дата создания документации
2025-01-27