# 📋 ОТЧЕТ #117: scripts/fix_long_lines.py

**Дата анализа:** 2025-09-16T00:07:18.593154
**Категория:** SCRIPT
**Статус:** ❌ 26 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 26
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/fix_long_lines.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 12 ошибок - Пробелы в пустых строках
- **E501:** 7 ошибок - Длинные строки (>79 символов)
- **F401:** 2 ошибок - Неиспользуемые импорты
- **E302:** 1 ошибок - Недостаточно пустых строк
- **F841:** 1 ошибок - Неиспользуемые переменные
- **F541:** 1 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F401:** Удалить неиспользуемые импорты
- **F841:** Удалить неиспользуемые переменные
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/fix_long_lines.py:8:1: F401 're' imported but unused
scripts/fix_long_lines.py:9:1: F401 'os' imported but unused
scripts/fix_long_lines.py:11:1: E302 expected 2 blank lines, found 1
scripts/fix_long_lines.py:14:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:17:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:21:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:23:9: F841 local variable 'original_line' is assigned to but never used
scripts/fix_long_lines.py:24:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:31:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:36:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:45:1: W293 blank line contains whitespace
scripts/fix_long_lines.py:52:80: E501 line too long (81 > 79 characters)
scripts/fix_long_lines.py:56:80: E501 line too long (133 > 79 characters)
scripts/fix_long_lines.py:60:1: W293 blank line contains whitespace
scripts/fix_long_lin
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:18.593286  
**Функция #117**
