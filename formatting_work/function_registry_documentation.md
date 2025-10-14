# Документация файла function_registry.json

## Информация о файле
- **Путь**: `/Users/sergejhlystov/ALADDIN_NEW/data/sfm/function_registry.json`
- **Тип файла**: JSON конфигурационный файл
- **Назначение**: Реестр функций системы SFM (Safe Function Manager)
- **Дата создания резервной копии**: 2025-01-27
- **Алгоритм**: Улучшенный алгоритм версии 2.5 с проверками

## Описание
Файл содержит JSON структуру с реестром всех функций системы безопасности ALADDIN. Включает:
- Метаданные функций
- Статусы функций (active, sleeping, running)
- Конфигурации безопасности
- Интеграционные данные

## Структура данных
```json
{
  "functions": {
    "function_id": {
      "function_id": "string",
      "name": "string", 
      "description": "string",
      "function_type": "string",
      "security_level": "string",
      "status": "string",
      "created_at": "datetime",
      "is_critical": "boolean",
      "auto_enable": "boolean",
      "wake_time": "datetime",
      "emergency_wake_up": "boolean"
    }
  }
}
```

## Текущие проблемы (предварительная оценка)
- Возможные проблемы форматирования JSON
- Длинные строки в описаниях
- Потенциальные проблемы с кодировкой
- Структурные проблемы валидации

## План обработки
1. Создание резервной копии ✅
2. Анализ структуры JSON
3. Проверка валидности JSON
4. Форматирование и очистка
5. Валидация структуры
6. Тестирование интеграции