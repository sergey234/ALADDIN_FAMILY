# 📋 ОТЧЕТ #219: scripts/safe_file_migration_plan.py

**Дата анализа:** 2025-09-16T00:08:08.716610
**Категория:** SCRIPT
**Статус:** ❌ 77 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 77
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/safe_file_migration_plan.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 47 ошибок - Пробелы в пустых строках
- **E501:** 16 ошибок - Длинные строки (>79 символов)
- **E302:** 6 ошибок - Недостаточно пустых строк
- **F541:** 6 ошибок - f-строки без плейсхолдеров
- **E305:** 1 ошибок - Ожидается 2 пустые строки после определения класса или функции
- **W292:** 1 ошибок - Нет новой строки в конце файла

### 🎯 Рекомендации по исправлению:

#### 🔴 КРИТИЧЕСКИЕ (исправить немедленно):
- **F541:** Заменить f-строки без плейсхолдеров на обычные

#### 🟡 ВАЖНЫЕ (исправить в ближайшее время):
- **E302:** Добавить пустые строки между функциями

#### 🟢 ФОРМАТИРОВАНИЕ (можно отложить):
- **W293:** Удалить пробелы в пустых строках
- **E501:** Разбить длинные строки на несколько коротких
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/safe_file_migration_plan.py:18:1: E302 expected 2 blank lines, found 1
scripts/safe_file_migration_plan.py:23:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:31:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:39:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:49:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:51:80: E501 line too long (94 > 79 characters)
scripts/safe_file_migration_plan.py:52:80: E501 line too long (99 > 79 characters)
scripts/safe_file_migration_plan.py:56:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:58:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:62:1: E302 expected 2 blank lines, found 1
scripts/safe_file_migration_plan.py:65:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:73:1: W293 blank line contains whitespace
scripts/safe_file_migration_plan.py:81:1: W293 blank
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:08:08.716749  
**Функция #219**
