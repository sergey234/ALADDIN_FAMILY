# 📋 ОТЧЕТ #98: scripts/disable_12_functions_sleep_mode.py

**Дата анализа:** 2025-09-16T00:07:12.257151
**Категория:** SCRIPT
**Статус:** ❌ 30 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 30
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/disable_12_functions_sleep_mode.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 12 ошибок - Пробелы в пустых строках
- **W291:** 8 ошибок - Пробелы в конце строки
- **F401:** 4 ошибок - Неиспользуемые импорты
- **E501:** 2 ошибок - Длинные строки (>79 символов)
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/disable_12_functions_sleep_mode.py:14:1: F401 'time' imported but unused
scripts/disable_12_functions_sleep_mode.py:16:1: F401 'typing.Dict' imported but unused
scripts/disable_12_functions_sleep_mode.py:16:1: F401 'typing.List' imported but unused
scripts/disable_12_functions_sleep_mode.py:16:1: F401 'typing.Any' imported but unused
scripts/disable_12_functions_sleep_mode.py:21:1: E302 expected 2 blank lines, found 1
scripts/disable_12_functions_sleep_mode.py:23:1: W293 blank line contains whitespace
scripts/disable_12_functions_sleep_mode.py:26:1: W293 blank line contains whitespace
scripts/disable_12_functions_sleep_mode.py:38:38: W291 trailing whitespace
scripts/disable_12_functions_sleep_mode.py:46:67: W291 trailing whitespace
scripts/disable_12_functions_sleep_mode.py:54:35: W291 trailing whitespace
scripts/disable_12_functions_sleep_mode.py:56:80: E501 line too long (82 > 79 characters)
scripts/disable_12_functions_sleep_mode.py:62:42: W291 trailing whitespace
scripts/di
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:12.257313  
**Функция #98**
