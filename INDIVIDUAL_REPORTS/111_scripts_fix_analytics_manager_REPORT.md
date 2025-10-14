# 📋 ОТЧЕТ #111: scripts/fix_analytics_manager.py

**Дата анализа:** 2025-09-16T00:07:16.713088
**Категория:** SCRIPT
**Статус:** ❌ 30 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 30
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/fix_analytics_manager.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 11 ошибок - Пробелы в пустых строках
- **E501:** 8 ошибок - Длинные строки (>79 символов)
- **F541:** 8 ошибок - f-строки без плейсхолдеров
- **F841:** 1 ошибок - Неиспользуемые переменные
- **W291:** 1 ошибок - Пробелы в конце строки
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F841:** Удалить неиспользуемые переменные
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/fix_analytics_manager.py:13:1: W293 blank line contains whitespace
scripts/fix_analytics_manager.py:16:1: W293 blank line contains whitespace
scripts/fix_analytics_manager.py:17:5: F841 local variable 'original_content' is assigned to but never used
scripts/fix_analytics_manager.py:19:1: W293 blank line contains whitespace
scripts/fix_analytics_manager.py:30:80: E501 line too long (87 > 79 characters)
scripts/fix_analytics_manager.py:32:80: E501 line too long (84 > 79 characters)
scripts/fix_analytics_manager.py:36:80: E501 line too long (86 > 79 characters)
scripts/fix_analytics_manager.py:40:80: E501 line too long (81 > 79 characters)
scripts/fix_analytics_manager.py:41:80: E501 line too long (102 > 79 characters)
scripts/fix_analytics_manager.py:42:80: E501 line too long (109 > 79 characters)
scripts/fix_analytics_manager.py:43:80: E501 line too long (111 > 79 characters)
scripts/fix_analytics_manager.py:52:1: W293 blank line contains whitespace
scripts/fix_analytics_manager
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:16.713209  
**Функция #111**
