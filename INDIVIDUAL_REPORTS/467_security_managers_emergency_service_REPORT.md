# 📋 ОТЧЕТ #467: security/managers/emergency_service.py

**Дата анализа:** 2025-09-16T00:10:02.380102
**Категория:** SECURITY
**Статус:** ❌ 61 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 61
- **Тип файла:** SECURITY
- **Путь к файлу:** `security/managers/emergency_service.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 44 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **E128:** 7 ошибок - Неправильные отступы
- **F401:** 1 ошибок - Неиспользуемые импорты
- **W291:** 1 ошибок - Пробелы в конце строки
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
security/managers/emergency_service.py:18:80: E501 line too long (80 > 79 characters)
security/managers/emergency_service.py:19:80: E501 line too long (90 > 79 characters)
security/managers/emergency_service.py:20:80: E501 line too long (82 > 79 characters)
security/managers/emergency_service.py:21:1: F401 'security.ai_agents.emergency_security_utils.EmergencySecurityUtils' imported but unused
security/managers/emergency_service.py:27:1: W293 blank line contains whitespace
security/managers/emergency_service.py:35:1: W293 blank line contains whitespace
security/managers/emergency_service.py:36:55: W291 trailing whitespace
security/managers/emergency_service.py:40:1: W293 blank line contains whitespace
security/managers/emergency_service.py:48:1: W293 blank line contains whitespace
security/managers/emergency_service.py:54:1: W293 blank line contains whitespace
security/managers/emergency_service.py:56:1: W293 blank line contains whitespace
security/managers/emergency_service.py:58:30: 
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:10:02.380270  
**Функция #467**
