# 📋 ОТЧЕТ #465: security/managers/analytics_manager.py

**Дата анализа:** 2025-09-16T00:10:01.194357
**Категория:** SECURITY
**Статус:** ❌ 16 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 16
- **Тип файла:** SECURITY
- **Путь к файлу:** `security/managers/analytics_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **F841:** 10 ошибок - Неиспользуемые переменные
- **W293:** 5 ошибок - Пробелы в пустых строках
- **F401:** 1 ошибок - Неиспользуемые импорты

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F841:** Удалить неиспользуемые переменные

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках

### 📝 Детальный вывод flake8:

```
security/managers/analytics_manager.py:11:1: F401 'time' imported but unused
security/managers/analytics_manager.py:42:1: W293 blank line contains whitespace
security/managers/analytics_manager.py:54:1: W293 blank line contains whitespace
security/managers/analytics_manager.py:91:1: W293 blank line contains whitespace
security/managers/analytics_manager.py:135:5: F841 local variable 'config' is assigned to but never used
security/managers/analytics_manager.py:136:5: F841 local variable 'analysis_type' is assigned to but never used
security/managers/analytics_manager.py:137:5: F841 local variable 'data_source' is assigned to but never used
security/managers/analytics_manager.py:138:5: F841 local variable 'time_window' is assigned to but never used
security/managers/analytics_manager.py:139:5: F841 local variable 'sample_size' is assigned to but never used
security/managers/analytics_manager.py:140:5: F841 local variable 'confidence_threshold' is assigned to but never used
security/manag
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:10:01.194910  
**Функция #465**
