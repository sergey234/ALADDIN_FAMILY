# 📋 ОТЧЕТ #395: security/ai_agents/smart_notification_manager_extra.py

**Дата анализа:** 2025-09-16T00:09:29.885349
**Категория:** AI_AGENT
**Статус:** ❌ 111 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 111
- **Тип файла:** AI_AGENT
- **Путь к файлу:** `security/ai_agents/smart_notification_manager_extra.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 56 ошибок - Пробелы в пустых строках
- **E501:** 35 ошибок - Длинные строки (>79 символов)
- **E302:** 6 ошибок - Недостаточно пустых строк
- **W291:** 4 ошибок - Пробелы в конце строки
- **E128:** 4 ошибок - Неправильные отступы
- **F401:** 3 ошибок - Неиспользуемые импорты
- **F811:** 1 ошибок - Переопределение импорта
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F811:** Удалить дублирующиеся импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
security/ai_agents/smart_notification_manager_extra.py:4:80: E501 line too long (86 > 79 characters)
security/ai_agents/smart_notification_manager_extra.py:7:1: F401 'numpy as np' imported but unused
security/ai_agents/smart_notification_manager_extra.py:9:1: F401 'time' imported but unused
security/ai_agents/smart_notification_manager_extra.py:11:1: F401 'typing.Optional' imported but unused
security/ai_agents/smart_notification_manager_extra.py:15:1: E302 expected 2 blank lines, found 1
security/ai_agents/smart_notification_manager_extra.py:23:1: E302 expected 2 blank lines, found 1
security/ai_agents/smart_notification_manager_extra.py:30:1: E302 expected 2 blank lines, found 1
security/ai_agents/smart_notification_manager_extra.py:38:1: E302 expected 2 blank lines, found 1
security/ai_agents/smart_notification_manager_extra.py:46:1: E302 expected 2 blank lines, found 1
security/ai_agents/smart_notification_manager_extra.py:54:1: E302 expected 2 blank lines, found 1
security/ai_agen
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:29.885542  
**Функция #395**
