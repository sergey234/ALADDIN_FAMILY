# 📋 ОТЧЕТ #53: scripts/auto_migration_no_input.py

**Дата анализа:** 2025-09-16T00:06:56.487543
**Категория:** SCRIPT
**Статус:** ❌ 45 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 45
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/auto_migration_no_input.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 24 ошибок - Пробелы в пустых строках
- **F541:** 11 ошибок - f-строки без плейсхолдеров
- **E302:** 6 ошибок - Недостаточно пустых строк
- **W291:** 1 ошибок - Пробелы в конце строки
- **E128:** 1 ошибок - Неправильные отступы
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями
- **E128:** Исправить отступы в коде

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/auto_migration_no_input.py:13:1: E302 expected 2 blank lines, found 1
scripts/auto_migration_no_input.py:17:1: W293 blank line contains whitespace
scripts/auto_migration_no_input.py:21:1: W293 blank line contains whitespace
scripts/auto_migration_no_input.py:25:1: E302 expected 2 blank lines, found 1
scripts/auto_migration_no_input.py:34:1: E302 expected 2 blank lines, found 1
scripts/auto_migration_no_input.py:36:66: W291 trailing whitespace
scripts/auto_migration_no_input.py:37:27: E128 continuation line under-indented for visual indent
scripts/auto_migration_no_input.py:45:1: E302 expected 2 blank lines, found 1
scripts/auto_migration_no_input.py:51:1: W293 blank line contains whitespace
scripts/auto_migration_no_input.py:57:19: F541 f-string is missing placeholders
scripts/auto_migration_no_input.py:59:1: W293 blank line contains whitespace
scripts/auto_migration_no_input.py:61:1: W293 blank line contains whitespace
scripts/auto_migration_no_input.py:67:19: F541 f-string is
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:06:56.487697  
**Функция #53**
