# 📋 ОТЧЕТ #232: scripts/show_all_sfm_functions.py

**Дата анализа:** 2025-09-16T00:08:13.728275
**Категория:** SCRIPT
**Статус:** ❌ 73 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 73
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/show_all_sfm_functions.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **E501:** 40 ошибок - Длинные строки (>79 символов)
- **W293:** 24 ошибок - Пробелы в пустых строках
- **F401:** 4 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **W291:** 1 ошибок - Пробелы в конце строки
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **E501:** Разбить длинные строки на несколько коротких
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/show_all_sfm_functions.py:9:1: F401 'os' imported but unused
scripts/show_all_sfm_functions.py:10:1: F401 'datetime.datetime' imported but unused
scripts/show_all_sfm_functions.py:16:5: F401 'security.safe_function_manager.FunctionStatus' imported but unused
scripts/show_all_sfm_functions.py:16:80: E501 line too long (82 > 79 characters)
scripts/show_all_sfm_functions.py:17:5: F401 'core.base.SecurityLevel' imported but unused
scripts/show_all_sfm_functions.py:22:1: E302 expected 2 blank lines, found 1
scripts/show_all_sfm_functions.py:26:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions.py:30:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions.py:35:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions.py:38:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions.py:42:1: W293 blank line contains whitespace
scripts/show_all_sfm_functions.py:50:1: W293 blank line contains whitespace
scripts/show_all_sfm_functio
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:13.728403  
**Функция #232**
