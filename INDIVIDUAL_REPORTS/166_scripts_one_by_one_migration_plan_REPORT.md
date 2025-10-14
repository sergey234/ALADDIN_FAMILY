# 📋 ОТЧЕТ #166: scripts/one_by_one_migration_plan.py

**Дата анализа:** 2025-09-16T00:07:47.827142
**Категория:** SCRIPT
**Статус:** ❌ 100 ошибок

## 📊 СТАТИСТИКА

- **Общее количество ошибок:** 100
- **Тип файла:** SCRIPT
- **Путь к файлу:** `scripts/one_by_one_migration_plan.py`

## ❌ ОБНАРУЖЕННЫЕ ОШИБКИ

### 📈 Распределение ошибок по типам:

- **W293:** 61 ошибок - Пробелы в пустых строках
- **F541:** 19 ошибок - f-строки без плейсхолдеров
- **E302:** 9 ошибок - Недостаточно пустых строк
- **E501:** 6 ошибок - Длинные строки (>79 символов)
- **W291:** 2 ошибок - Пробелы в конце строки
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
- **E501:** Разбить длинные строки на несколько коротких
- **W291:** Удалить пробелы в конце строк
- **W292:** Добавить новую строку в конце файла

### 📝 Детальный вывод flake8:

```
scripts/one_by_one_migration_plan.py:18:1: E302 expected 2 blank lines, found 1
scripts/one_by_one_migration_plan.py:22:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:26:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:30:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:35:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:36:15: F541 f-string is missing placeholders
scripts/one_by_one_migration_plan.py:40:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:44:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:46:80: E501 line too long (84 > 79 characters)
scripts/one_by_one_migration_plan.py:51:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:59:1: W293 blank line contains whitespace
scripts/one_by_one_migration_plan.py:64:1: E302 expected 2 blank lines, found 1
scripts/one_by_one_migration_plan.py:67:1:
... (показаны первые 1000 символов)
```

---
**Отчет создан:** AI Security Assistant  
**Дата:** 2025-09-16T00:07:47.827366  
**Функция #166**
