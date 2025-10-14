# 📋 ОТЧЕТ #238: scripts/simple_show_functions.py

**Дата анализа:** 2025-09-16T00:08:15.772537
**Категория:** SCRIPT
**Статус:** ❌ 42 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 42
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/simple_show_functions.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 15 ошибок - Пробелы в пустых строках
- **E501:** 12 ошибок - Длинные строки (>79 символов)
- **W291:** 9 ошибок - Пробелы в конце строки
- **F401:** 2 ошибок - Неиспользуемые импорты
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
scripts/simple_show_functions.py:9:1: F401 'os' imported but unused
scripts/simple_show_functions.py:10:1: F401 'datetime.datetime' imported but unused
scripts/simple_show_functions.py:15:1: E302 expected 2 blank lines, found 1
scripts/simple_show_functions.py:19:1: W293 blank line contains whitespace
scripts/simple_show_functions.py:24:32: W291 trailing whitespace
scripts/simple_show_functions.py:34:45: W291 trailing whitespace
scripts/simple_show_functions.py:44:41: W291 trailing whitespace
scripts/simple_show_functions.py:54:38: W291 trailing whitespace
scripts/simple_show_functions.py:69:37: W291 trailing whitespace
scripts/simple_show_functions.py:86:1: W293 blank line contains whitespace
scripts/simple_show_functions.py:99:46: W291 trailing whitespace
scripts/simple_show_functions.py:111:36: W291 trailing whitespace
scripts/simple_show_functions.py:145:42: W291 trailing whitespace
scripts/simple_show_functions.py:225:1: W293 blank line contains whitespace
scripts/simple_show_func
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:15.772661  
**Функция #238**
