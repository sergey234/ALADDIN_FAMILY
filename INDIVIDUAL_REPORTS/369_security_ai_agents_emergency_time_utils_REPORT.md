# 📋 ОТЧЕТ #369: security/ai_agents/emergency_time_utils.py

**Дата анализа:** 2025-09-16T00:09:17.268243
**Категория:** AI_AGENT
**Статус:** ❌ 47 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 47
- **Тип файла:** AI_AGENT
- **Путь к файлу:** `security/ai_agents/emergency_time_utils.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 38 ошибок - Пробелы в пустых строках
- **W291:** 3 ошибок - Пробелы в конце строки
- **E128:** 3 ошибок - Неправильные отступы
- **F401:** 2 ошибок - Неиспользуемые импорты
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
security/ai_agents/emergency_time_utils.py:8:1: F401 'datetime.timedelta' imported but unused
security/ai_agents/emergency_time_utils.py:9:1: F401 'typing.Optional' imported but unused
security/ai_agents/emergency_time_utils.py:14:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:18:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:23:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:26:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:31:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:36:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:39:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:44:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:49:1: W293 blank line contains whitespace
security/ai_agents/emergency_time_utils.py:52:1: W
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:09:17.268407  
**Функция #369**
