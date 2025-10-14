# 📋 ОТЧЕТ #235: scripts/simple_disable_functions.py

**Дата анализа:** 2025-09-16T00:08:14.684040
**Категория:** SCRIPT
**Статус:** ❌ 18 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 18
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/simple_disable_functions.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 11 ошибок - Пробелы в пустых строках
- **E261:** 2 ошибок - Ошибка E261
- **E302:** 1 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E501:** 1 ошибок - Длинные строки (>79 символов)
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/simple_disable_functions.py:11:1: E302 expected 2 blank lines, found 1
scripts/simple_disable_functions.py:15:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:19:49: W291 trailing whitespace
scripts/simple_disable_functions.py:28:34: E261 at least two spaces before inline comment
scripts/simple_disable_functions.py:29:41: E261 at least two spaces before inline comment
scripts/simple_disable_functions.py:31:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:35:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:37:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:42:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:43:80: E501 line too long (101 > 79 characters)
scripts/simple_disable_functions.py:45:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:76:1: W293 blank line contains whitespace
scripts/simple_disable_functions.py:80:1: W
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:14.684154  
**Функция #235**
