# 📋 ОТЧЕТ #469: security/managers/report_manager.py

**Дата анализа:** 2025-09-16T00:10:03.580884
**Категория:** SECURITY
**Статус:** ❌ 31 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 31
- **Тип файла:** SECURITY
- **Путь к файлу:** `security/managers/report_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 16 ошибок - Пробелы в пустых строках
- **E501:** 13 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких

### 📝 Детальный вывод flake8:

```
security/managers/report_manager.py:7:1: F401 'pandas as pd' imported but unused
security/managers/report_manager.py:9:1: F401 'security.base.SecurityBase' imported but unused
security/managers/report_manager.py:44:1: W293 blank line contains whitespace
security/managers/report_manager.py:45:80: E501 line too long (91 > 79 characters)
security/managers/report_manager.py:86:1: W293 blank line contains whitespace
security/managers/report_manager.py:91:1: W293 blank line contains whitespace
security/managers/report_manager.py:96:80: E501 line too long (81 > 79 characters)
security/managers/report_manager.py:101:1: W293 blank line contains whitespace
security/managers/report_manager.py:112:1: W293 blank line contains whitespace
security/managers/report_manager.py:117:80: E501 line too long (80 > 79 characters)
security/managers/report_manager.py:121:80: E501 line too long (82 > 79 characters)
security/managers/report_manager.py:122:1: W293 blank line contains whitespace
security/managers/r
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:10:03.581047  
**Функция #469**
