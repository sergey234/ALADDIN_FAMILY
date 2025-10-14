# 📋 ОТЧЕТ #291: scripts/test_regex_search.py

**Дата анализа:** 2025-09-16T00:08:37.813880
**Категория:** SCRIPT
**Статус:** ❌ 69 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 69
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/test_regex_search.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 40 ошибок - Пробелы в пустых строках
- **E501:** 10 ошибок - Длинные строки (>79 символов)
- **F401:** 5 ошибок - Неиспользуемые импорты
- **W291:** 4 ошибок - Пробелы в конце строки
- **E128:** 4 ошибок - Неправильные отступы
- **E402:** 2 ошибок - Импорты не в начале файла
- **F541:** 2 ошибок - f-строки без плейсхолдеров
- **F841:** 1 ошибок - Неиспользуемые переменные
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F541:** Заменить f-строки без плейсхолдеров на обычные
- **F841:** Удалить неиспользуемые переменные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E402:** Переместить импорты в начало файла
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/test_regex_search.py:13:1: F401 'json' imported but unused
scripts/test_regex_search.py:21:1: F401 'elasticsearch_simulator.LogLevel' imported but unused
scripts/test_regex_search.py:21:1: F401 'elasticsearch_simulator.LogEntry' imported but unused
scripts/test_regex_search.py:21:1: E402 module level import not at top of file
scripts/test_regex_search.py:22:1: F401 'datetime.datetime' imported but unused
scripts/test_regex_search.py:22:1: F401 'datetime.timedelta' imported but unused
scripts/test_regex_search.py:22:1: E402 module level import not at top of file
scripts/test_regex_search.py:31:1: W293 blank line contains whitespace
scripts/test_regex_search.py:34:1: W293 blank line contains whitespace
scripts/test_regex_search.py:76:1: W293 blank line contains whitespace
scripts/test_regex_search.py:79:1: W293 blank line contains whitespace
scripts/test_regex_search.py:87:1: W293 blank line contains whitespace
scripts/test_regex_search.py:90:1: W293 blank line contains whitespac
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:37.814014  
**Функция #291**
